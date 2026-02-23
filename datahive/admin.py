from django.contrib import admin

from .models import Documents, Tags, Categories
from .model_enhanced import RichDocuments


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'organization')


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'organization', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active', 'organization')


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'organization', 'project', 'category', 'is_public', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_public', 'organization', 'project', 'category')


@admin.register(RichDocuments)
class RichDocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'organization', 'project', 'category', 'is_public', 'is_template', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_public', 'is_template', 'organization', 'project', 'category')
