from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.signup_view, name='signup'),
    path('blogpost/', views.blogpost, name='blogpost'),
    path('post/', views.blog_home, name='post'),
    path('home/', views.blog_home, name='blog_home'),
    path('logout/', views.logout_view, name='logout'),
    path('myposts/', views.user_posts, name='user_posts'),
    path('myposts/edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('myposts/delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('comment/<int:comment_id>/vote/', views.toggle_comment_vote, name='toggle_comment_vote'),

]
