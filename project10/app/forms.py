from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import BlogPost, Comment

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    class Meta:
        fields = ['username', 'password']
        
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class BlogPostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': "What's on your mind?",
            'rows': 5,
            'id': 'blog_text'
        }),
        
        max_length=1000,
        label=''
    )

    class Meta:
        model = BlogPost
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter title here',
                'style': 'padding:10px; font-size:1.2em; width:100%; border-radius:8px; border:1px solid #444; background:#252525; color:#fff; margin-bottom:20px;'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': "What's on your mind?",
                'style': 'padding:10px; font-size:1.2em; width:100%; border-radius:8px; border:1px solid #444; background:#252525; color:#fff; margin-bottom:20px;'
            }),
        }
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'})
        }