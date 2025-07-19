from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models # Added: Needed for models.F in post_detail
from django.utils.text import slugify # Added: Needed for slugify in blogpost
from django.utils import timezone # Added: Needed for timezone in blogpost
from django.views.decorators.http import require_POST
from django.db.models import Count

from .models import BlogPost, Comment # Added: Ensure Comment is imported
from .forms import LoginForm, SignUpForm, BlogPostForm, CommentForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('blog_home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('blog_home')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()

    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('blog_home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('blog_home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'app/login.html', {'form': form})

@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

@login_required
def blog_home(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, 'Your post has been published!')
            return redirect('blog_home')
        else:
            messages.error(request, 'There was an error with your post.')
            print("Form errors:", form.errors)
    else:
        form = BlogPostForm()

    # Get all posts ordered by creation date (newest first)
    posts = BlogPost.objects.all().order_by('-created_at')
    
    return render(request, 'app/blogpost.html', {
        'form': form,
        'posts': posts,
        'user': request.user
    })

@login_required
def user_posts(request):
    # Get only the current user's posts
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'app/user_posts.html', {'posts': posts})

@login_required
def blogpost(request):
    if request.method == 'POST':
        content = request.POST.get('blog')
        if content:
            BlogPost.objects.create(
                author=request.user,
                content=content,
                # Ensure BlogPost model has 'title' or 'content' field to slugify
                # If only content is available, using a snippet might be better
                slug=slugify(content[:30] + str(timezone.now().timestamp())) 
            )
            return redirect('blogpost')
    
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'app/blogpost.html', {'posts': posts})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('user_posts')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'app/edit_post.html', {'form': form})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('user_posts')
    return render(request, 'app/delete_post.html', {'post': post})

@require_POST
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    liked = False
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})
    
@require_POST
@login_required
def comment_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post_detail', pk=post.id)
    else:
        # Instead of rendering, it's generally better to redirect and use messages
        messages.error(request, 'Invalid comment. Please try again.')
        return redirect('post_detail', pk=post.id)
    
def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    # top-level comments only (no parent)
    top_comments_qs = (
        post.comments
            .filter(parent__isnull=True)
            .annotate(
                likes_count=Count('likes', distinct=True),
                dislikes_count=Count('dislikes', distinct=True),
            )
            .order_by('-likes_count', '-created_at')  # tweak ordering if you want
            .prefetch_related('author', 'likes', 'dislikes', 'replies__author', 'replies__likes', 'replies__dislikes')
    )

    # just pass the queryset; template can check membership like:
    # {% if request.user in comment.likes.all %} …
    context = {
        'post': post,
        'top_comments': top_comments_qs,
        'form': CommentForm(),
    }
    return render(request, 'app/post_detail.html', context)

@login_required
def toggle_comment_vote(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    action = request.POST.get('action')  # 'like' or 'dislike'

    liked_status = False
    disliked_status = False

    if action == 'like':
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            liked_status = False
        else:
            comment.likes.add(request.user)
            # Ensure user cannot like and dislike the same comment simultaneously
            comment.dislikes.remove(request.user)
            liked_status = True
    elif action == 'dislike':
        if request.user in comment.dislikes.all():
            comment.dislikes.remove(request.user)
            disliked_status = False
        else:
            comment.dislikes.add(request.user)
            # Ensure user cannot dislike and like the same comment simultaneously
            comment.likes.remove(request.user)
            disliked_status = True
    
    # Calculate current score after the vote change
    # This assumes your Comment model has a 'score' property/method or you calculate it here.
    # For now, using direct calculation:
    current_score = comment.likes.count() - comment.dislikes.count()

    return JsonResponse({
        'liked': liked_status,
        'disliked': disliked_status,
        'score': current_score,
        'like_count': comment.likes.count(),
        'dislike_count': comment.dislikes.count(),
    })