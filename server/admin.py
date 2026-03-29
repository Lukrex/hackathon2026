from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import (
    Category,
    Skill,
    Language,
    Expert,
    Request,
    ExpertMatch,
    Notification,
    RequestChatMessage,
    AdminChatMessage,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = ['name', 'skills_display', 'is_busy', 'rating', 'karma_points', 'help_provided', 'created_at']
    list_filter = ['is_busy', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'skills__name', 'languages__name']
    readonly_fields = ['created_at', 'help_provided', 'karma_points']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'profile_image', 'bio', 'work_experience', 'skills', 'languages', 'is_busy')
        }),
        ('Ratings', {
            'fields': ('rating', 'rating_count', 'karma_points', 'help_provided', 'created_at'),
        }),
    )
    def name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    name.short_description = 'Meno'

    def skills_display(self, obj):
        """Display skills as nice tags"""
        tags = obj.get_skill_list()
        html = ' '.join([
            f'<span style="background: #667eea30; padding: 2px 8px; border-radius: 4px; margin: 2px;">{tag}</span>'
            for tag in tags
        ])
        return format_html(html)
    skills_display.short_description = 'Skills'


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_title',
        'priority_badge',
        'status_badge',
        'category',
        'requester_name',
        'created_at',
        'review_status'
    ]
    list_filter = ['priority', 'status', 'category', 'created_at']
    search_fields = ['title', 'description', 'requester_name', 'requester_email']

    fieldsets = (
        ('Request Details', {
            'fields': (
                'title', 'description', 'category', 'priority', 'value_score',
                'requester_type', 'requester_name', 'requester_email', 'requester_phone',
                'is_corporate', 'company_name', 'company_email', 'due_date',
                'target_skills', 'required_languages', 'target_experience'
            )
        }),
        ('Status', {
            'fields': ('status', 'resolved_at', 'resolution_notes'),
        }),
        ('Matching', {
            'fields': ('assigned_experts',),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('reviewed_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'reviewed_by']
    filter_horizontal = ['assigned_experts', 'target_skills', 'required_languages']
    actions = ['mark_in_review', 'mark_in_progress', 'mark_resolved', 'mark_rejected']

    def request_title(self, obj):
        return obj.title
    request_title.short_description = 'Názov žiadosti'

    def priority_badge(self, obj):
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#0dcaf0',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priorita'

    def status_badge(self, obj):
        colors = {
            'open': '#198754',
            'in_review': '#0d6efd',
            'waiting_expert': '#0dcaf0',
            'in_progress': '#fd7e14',
            'resolved': '#6c757d',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def review_status(self, obj):
        if obj.reviewed_by:
            return format_html(
                '✅ Overené ({}) - {}',
                obj.reviewed_by.get_full_name(),
                'by admin'
            )
        return format_html('<span style="color: #6c757d;">⏳ V čakaní na preverenie</span>')
    review_status.short_description = 'Preverenie'

    def save_model(self, request, obj, form, change):
        """Auto-set reviewed_by when saving"""
        if change and not obj.reviewed_by:
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)

    def mark_in_review(self, request, queryset):
        updated = queryset.update(status='in_review', reviewed_by=request.user)
        self.message_user(request, f'{updated} žiadostí bolo označených ako "V preverovaní"')
    mark_in_review.short_description = '📋 Označiť ako "V preverovaní"'

    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} žiadostí je teraz "V riešení"')
    mark_in_progress.short_description = '🔧 Označiť ako "V riešení"'

    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} žiadostí bolo vyriešených')
    mark_resolved.short_description = '✅ Označiť ako "Vyriešené"'

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} žiadostí bolo zamietnutých')
    mark_rejected.short_description = '❌ Označiť ako "Zamietnuté"'


@admin.register(ExpertMatch)
class ExpertMatchAdmin(admin.ModelAdmin):
    list_display = ['request_title', 'expert_name', 'match_score_display', 'created_at']
    list_filter = ['created_at', 'request__priority']
    search_fields = ['request__title', 'expert__user__first_name', 'expert__user__last_name']
    readonly_fields = ['created_at', 'match_score_display_chart']

    fieldsets = (
        ('Návrh', {
            'fields': ('request', 'expert')
        }),
        ('Skóre zhody', {
            'fields': ('match_score', 'match_score_display_chart'),
        }),
        ('Zdôvodnenie', {
            'fields': ('reasoning',),
        }),
    )

    def request_title(self, obj):
        return obj.request.title
    request_title.short_description = 'Žiadosť'

    def expert_name(self, obj):
        return obj.expert.user.get_full_name()
    expert_name.short_description = 'Expert'

    def match_score_display(self, obj):
        """Visual score display"""
        color = 'green' if obj.match_score >= 70 else 'orange' if obj.match_score >= 50 else 'red'
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{:.0f}%</span>',
            color,
            obj.match_score
        )
    match_score_display.short_description = 'Skóre zhody'

    def match_score_display_chart(self, obj):
        """Visual progress bar"""
        width = int(obj.match_score)
        return format_html(
            '<div style="background: #e9ecef; border-radius: 4px; height: 20px; width: 100%; '
            'overflow: hidden;"><div style="background: linear-gradient(90deg, #667eea, #764ba2); '
            'height: 100%; width: {}%; display: flex; align-items: center; justify-content: center; '
            'color: white; font-size: 12px; font-weight: bold;">{:.0f}%</div></div>',
            width,
            obj.match_score
        )
    match_score_display_chart.short_description = 'Skóre'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_type', 'recipient_email', 'request_title', 'sent_at']
    list_filter = ['notification_type', 'sent_at']
    search_fields = ['recipient_email', 'request__title']
    readonly_fields = ['request', 'recipient_email', 'notification_type', 'subject', 'sent_at']

    def request_title(self, obj):
        return obj.request.title
    request_title.short_description = 'Žiadosť'

    def has_add_permission(self, request):
        """Prevent manual notification creation"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup"""
        return True


@admin.register(RequestChatMessage)
class RequestChatMessageAdmin(admin.ModelAdmin):
    list_display = ['request', 'sender', 'created_at']
    list_filter = ['created_at']
    search_fields = ['request__title', 'sender__username', 'sender__email', 'message']
    readonly_fields = ['request', 'sender', 'message', 'created_at']

    def has_add_permission(self, request):
        return False


@admin.register(AdminChatMessage)
class AdminChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sender__username', 'sender__email', 'message']
    readonly_fields = ['sender', 'message', 'created_at']

    def has_add_permission(self, request):
        return False
