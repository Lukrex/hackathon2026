from .chat_utils import get_unread_chat_count, is_company_account


def chat_nav_badge(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated or not is_company_account(user):
        return {
            'chats_unread_count': 0,
            'chats_has_unread': False,
        }

    unread_count = get_unread_chat_count(user)
    return {
        'chats_unread_count': unread_count,
        'chats_has_unread': unread_count > 0,
    }
