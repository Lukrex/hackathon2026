from django.utils import timezone

from .models import (
    AdminChatMessage,
    ChatMuteSetting,
    ChatReadState,
    CompanyChatMessage,
    DirectChatMessage,
)


CHAT_COMPANY = 'company'
CHAT_ADMIN = 'admin'
CHAT_DIRECT = 'direct'


def is_company_account(user):
    return bool(user and user.is_authenticated and user.is_active and (user.is_staff or user.is_superuser))


def is_chat_muted(user, chat_type, partner=None):
    return ChatMuteSetting.objects.filter(
        user=user,
        chat_type=chat_type,
        partner=partner,
        is_muted=True,
    ).exists()


def set_chat_muted(user, chat_type, is_muted, partner=None):
    ChatMuteSetting.objects.update_or_create(
        user=user,
        chat_type=chat_type,
        partner=partner,
        defaults={'is_muted': bool(is_muted)},
    )


def mark_chat_read(user, chat_type, partner=None):
    ChatReadState.objects.update_or_create(
        user=user,
        chat_type=chat_type,
        partner=partner,
        defaults={'last_read_at': timezone.now()},
    )


def _last_read_at(user, chat_type, partner=None):
    state = ChatReadState.objects.filter(
        user=user,
        chat_type=chat_type,
        partner=partner,
    ).first()
    if state:
        return state.last_read_at
    return None


def get_unread_chat_count(user):
    """Count unread chat channels/threads for nav badge (respects mute settings)."""
    if not is_company_account(user):
        return 0

    unread_count = 0

    if not is_chat_muted(user, CHAT_COMPANY):
        company_qs = CompanyChatMessage.objects.exclude(sender=user)
        company_last_read = _last_read_at(user, CHAT_COMPANY)
        if company_last_read:
            company_qs = company_qs.filter(created_at__gt=company_last_read)
        if company_qs.exists():
            unread_count += 1

    if user.is_superuser and not is_chat_muted(user, CHAT_ADMIN):
        admin_qs = AdminChatMessage.objects.exclude(sender=user)
        admin_last_read = _last_read_at(user, CHAT_ADMIN)
        if admin_last_read:
            admin_qs = admin_qs.filter(created_at__gt=admin_last_read)
        if admin_qs.exists():
            unread_count += 1

    if user.is_superuser:
        partners = user.__class__.objects.filter(is_staff=True, is_superuser=False).only('id')
    else:
        partners = user.__class__.objects.filter(is_superuser=True).only('id')

    for partner in partners:
        if is_chat_muted(user, CHAT_DIRECT, partner=partner):
            continue

        direct_qs = DirectChatMessage.objects.filter(
            sender=partner,
            recipient=user,
        )
        direct_last_read = _last_read_at(user, CHAT_DIRECT, partner=partner)
        if direct_last_read:
            direct_qs = direct_qs.filter(created_at__gt=direct_last_read)
        if direct_qs.exists():
            unread_count += 1

    return unread_count
