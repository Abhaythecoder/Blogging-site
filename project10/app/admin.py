from django.contrib import admin
from .models import BlogPost, UserProfile


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'created_at']
    fields = ['author', 'title', 'content', 'slug']
    prepopulated_fields = {'slug': ('title',)}  # auto fill slug from title


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location']
    fields = ['user', 'bio', 'profile_picture', 'website', 'location']
