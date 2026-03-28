from rest_framework import serializers
from .models import Category, Expert, Request, ExpertMatch, Notification


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon']


class ExpertSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    expertise_list = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = [
            'id', 'full_name', 'bio', 'expertise', 'expertise_list',
            'availability', 'help_provided', 'profile_image'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_expertise_list(self, obj):
        return obj.get_expertise_list()


class ExpertMatchSerializer(serializers.ModelSerializer):
    expert_detail = ExpertSerializer(source='expert', read_only=True)

    class Meta:
        model = ExpertMatch
        fields = ['id', 'expert', 'expert_detail', 'match_score', 'reasoning', 'created_at']


class RequestDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_experts = ExpertSerializer(many=True, read_only=True)
    suggested_matches = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = [
            'id', 'title', 'description', 'requester_name', 'requester_email',
            'requester_phone', 'category', 'category_display', 'priority',
            'priority_display', 'status', 'status_display', 'value_score',
            'review_notes', 'assigned_experts', 'suggested_matches',
            'created_at', 'updated_at', 'resolved_at', 'resolution_notes',
            'reviewer_name'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'resolved_at',
            'assigned_experts', 'suggested_matches'
        ]

    def get_suggested_matches(self, obj):
        """Get top 3 expert matches"""
        matches = obj.expert_matches.all()[:3]
        return ExpertMatchSerializer(matches, many=True).data

    def get_reviewer_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        return None


class RequestListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    expert_count = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = [
            'id', 'title', 'requester_name', 'category', 'category_display',
            'priority', 'priority_display', 'status', 'status_display',
            'value_score', 'expert_count', 'created_at'
        ]

    def get_expert_count(self, obj):
        return obj.assigned_experts.count()


class RequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new requests via public API"""

    class Meta:
        model = Request
        fields = [
            'title', 'description', 'requester_name', 'requester_email',
            'requester_phone', 'category'
        ]

    def create(self, validated_data):
        request_obj = Request.objects.create(
            status='open',
            priority='medium',  # Default, will be set manually
            **validated_data
        )
        # Send confirmation email automatically
        from .tasks import send_confirmation_email
        send_confirmation_email.delay(request_obj.id)
        return request_obj


class NotificationSerializer(serializers.ModelSerializer):
    request_title = serializers.CharField(source='request.title', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'request', 'request_title', 'recipient_email',
            'notification_type', 'subject', 'sent_at'
        ]
