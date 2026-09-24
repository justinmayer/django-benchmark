from django.contrib import admin
from .models import Ticket, Comment, PullRequest, Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'component', 'queue', 'created_at')
    list_filter = ('queue', 'component', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'ticket', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author', 'content')
    date_hierarchy = 'created_at'


@admin.register(PullRequest)
class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('pr_number', 'ticket', 'created_at')
    search_fields = ('pr_number', 'ticket__title')
    date_hierarchy = 'created_at'
