from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """Request category"""
    CATEGORY_CHOICES = [
        ('hiring', '🔍 Hľadanie zamestnanca'),
        ('investment', '💰 Hľadanie investora'),
        ('consulting', '📊 Konzultácia'),
        ('marketing', '📢 Marketing pomoc'),
        ('speaking', '🎤 Speaking príležitosť'),
        ('networking', '🤝 Networking'),
        ('sales', '💼 Sales podpora'),
        ('other', '❓ Ostatné'),
    ]

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='❓')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.get_name_display()


class Expert(models.Model):
    """Community expert/helper"""
    AVAILABILITY_CHOICES = [
        ('high', 'Vysoká (hoc-aj denne)'),
        ('medium', 'Stredná (niekoľko hodín mesiac)'),
        ('low', 'Nízka (len keď je čas)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    expertise = models.CharField(
        max_length=500,
        help_text="Odbornosti oddelené čiarkami (napr: React, Python, GTM, Sales)"
    )
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='medium'
    )
    help_provided = models.IntegerField(default=0, help_text="Počet pomôcok, ktoré poskytol")
    profile_image = models.ImageField(upload_to='experts/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def get_expertise_list(self):
        """Return expertise as list"""
        return [e.strip() for e in self.expertise.split(',')]


class Request(models.Model):
    """Help request from community member"""
    STATUS_CHOICES = [
        ('open', '🟢 Otvorená'),
        ('in_review', '🟡 V preverovaní'),
        ('waiting_expert', '⏳ Čakanie na experta'),
        ('in_progress', '🟠 V riešení'),
        ('resolved', '✅ Vyriešená'),
        ('rejected', '❌ Zamietnutá'),
    ]

    PRIORITY_CHOICES = [
        ('low', '🔵 Nízka'),
        ('medium', '🟡 Stredná'),
        ('high', '🔴 Vysoká'),
        ('critical', '🔴🔴 Kritická'),
    ]

    REQUESTER_TYPE_CHOICES = [
        ('startup', '🚀 Startup'),
        ('investor', '💰 Investor'),
        ('service_provider', '🛠️ Poskytovateľ služieb'),
        ('community_member', '👥 Člen komunity'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    requester_name = models.CharField(max_length=200)
    requester_email = models.EmailField()
    requester_phone = models.CharField(max_length=20, blank=True)
    requester_type = models.CharField(
        max_length=20,
        choices=REQUESTER_TYPE_CHOICES,
        default='community_member'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    value_score = models.IntegerField(
        default=5,
        help_text="Očakávaný vplyv / hodnota (1-10)"
    )

    # Admin review
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests'
    )
    review_notes = models.TextField(blank=True)

    # Matching
    assigned_experts = models.ManyToManyField(
        Expert,
        blank=True,
        related_name='assigned_requests'
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"

    def assign_expert(self, expert):
        """Assign expert to request"""
        self.assigned_experts.add(expert)
        # Send notification email
        from .tasks import send_expert_assignment_email
        send_expert_assignment_email.delay(self.id, expert.id)

    def resolve(self, notes=''):
        """Mark request as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()


class ExpertMatch(models.Model):
    """Smart match suggestion between request and expert"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='expert_matches')
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    match_score = models.FloatField(
        default=0,
        help_text="Match score 0-100%"
    )
    reasoning = models.TextField(blank=True, help_text="Dôvod návrhu")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request', 'expert')
        ordering = ['-match_score']

    def __str__(self):
        return f"{self.request.title} → {self.expert} ({self.match_score}%)"


class Notification(models.Model):
    """Email notifications tracking"""
    REQUEST_NOTIFICATION_TYPES = [
        ('confirmation', 'Potvrdenie žiadosti'),
        ('expert_match', 'Match s expertem'),
        ('status_update', 'Aktualizácia statusu'),
        ('resolved', 'Žiadosť vyriešená'),
    ]

    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    notification_type = models.CharField(max_length=50, choices=REQUEST_NOTIFICATION_TYPES)
    subject = models.CharField(max_length=200)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} → {self.recipient_email}"
