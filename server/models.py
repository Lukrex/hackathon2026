from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """Request category"""
    CATEGORY_CHOICES = [
        ('hiring', 'Hiring'),
        ('investment', 'Investment'),
        ('consulting', 'Consulting'),
        ('marketing', 'Marketing'),
        ('speaking', 'Speaking'),
        ('networking', 'Networking'),
        ('sales', 'Sales'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='❓')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.get_name_display()


class Skill(models.Model):
    """Skill tag for experts and request targets"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name


class Language(models.Model):
    """Language tag for expert profiles and request requirements"""
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def __str__(self):
        return self.name


class Expert(models.Model):
    """Community expert/helper (user profile)"""
    AVAILABILITY_CHOICES = [
        ('high', 'High (daily)'),
        ('medium', 'Medium (weekly)'),
        ('low', 'Low (occasional)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name='experts')
    languages = models.ManyToManyField(Language, blank=True, related_name='experts')
    work_experience = models.TextField(blank=True, help_text='Work experience highlights')
    rating = models.FloatField(default=0.0, help_text='Average user rating (0-5)')
    rating_count = models.IntegerField(default=0, help_text='Number of ratings')
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='medium'
    )
    help_provided = models.IntegerField(default=0, help_text='Number of help contributions')
    profile_image = models.ImageField(upload_to='experts/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def average_rating(self):
        return round(self.rating, 2) if self.rating_count > 0 else 0.0

    def get_skill_list(self):
        return [skill.name for skill in self.skills.all()]

    def get_language_list(self):
        return [language.name for language in self.languages.all()]


class Request(models.Model):
    """Help request from community member or corporation"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_review', 'In Review'),
        ('waiting_expert', 'Waiting for Expert'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    REQUESTER_TYPE_CHOICES = [
        ('corporate', 'Corporate'),
        ('startup', 'Startup'),
        ('investor', 'Investor'),
        ('service_provider', 'Service Provider'),
        ('community_member', 'Community Member'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('junior', 'Junior'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Corporate request fields
    is_corporate = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True)
    company_email = models.EmailField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    target_skills = models.ManyToManyField(Skill, blank=True, related_name='target_requests')
    required_languages = models.ManyToManyField(Language, blank=True, related_name='required_by_requests')
    target_experience = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True)

    # requester profile/reference
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
        help_text='Impact score (1-10)'
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

    # Who submitted this request (if a logged-in user)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_requests'
    )

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
