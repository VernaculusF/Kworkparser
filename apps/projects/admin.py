from django.contrib import admin
from .models import Category, Project


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'kwork_id', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'kwork_id']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'status', 'is_viewed', 'parsed_at']
    list_filter = ['status', 'is_viewed', 'category', 'parsed_at']
    search_fields = ['title', 'description', 'author_name', 'kwork_id']
    list_editable = ['status', 'is_viewed']
    readonly_fields = ['kwork_id', 'parsed_at', 'created_at', 'updated_at']
    date_hierarchy = 'parsed_at'
    ordering = ['-parsed_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'kwork_id', 'url')
        }),
        ('Детали заказа', {
            'fields': ('price', 'currency', 'deadline', 'author_name', 'author_rating')
        }),
        ('Статус', {
            'fields': ('status', 'is_viewed')
        }),
        ('Даты', {
            'fields': ('parsed_at', 'published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_viewed', 'mark_as_new', 'mark_as_responded', 'archive']
    
    def mark_as_viewed(self, request, queryset):
        queryset.update(status='viewed', is_viewed=True)
    mark_as_viewed.short_description = "Отметить как просмотренные"
    
    def mark_as_new(self, request, queryset):
        queryset.update(status='new', is_viewed=False)
    mark_as_new.short_description = "Отметить как новые"
    
    def mark_as_responded(self, request, queryset):
        queryset.update(status='responded')
    mark_as_responded.short_description = "Отметить отклик отправлен"
    
    def archive(self, request, queryset):
        queryset.update(status='archived')
    archive.short_description = "Архивировать"
