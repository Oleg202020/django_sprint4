from django.contrib import admin

from .models import Category, Comment, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'is_published',
        'created_at',
        'author',
        'location',
        'category',
    )
    list_filter = (
        'is_published',
    )
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    search_fields = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'description',
        'created_at',
    )
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'created_at',
        'text',
        'is_published',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
