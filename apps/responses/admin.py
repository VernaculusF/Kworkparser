from django.contrib import admin
from .models import Response


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['project', 'status', 'sent_at', 'result']
    list_filter = ['status', 'sent_at']
    search_fields = ['project__title', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'sent_at'
    ordering = ['-sent_at']
    
    fieldsets = (
        ('Отклик', {
            'fields': ('project', 'sent_at', 'status', 'result')
        }),
        ('Заметки', {
            'fields': ('notes',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
