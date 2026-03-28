from django import forms
from .models import Request, Category


class RequestSubmissionForm(forms.ModelForm):
    """Form for submitting new help requests"""

    class Meta:
        model = Request
        fields = [
            'title', 'description', 'requester_name',
            'requester_email', 'requester_phone', 'category'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Čo potrebuješ? (napr: Hľadám React vývojára)',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Podrobný popis tvej potreby...',
                'rows': 6
            }),
            'requester_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tvoje meno'
            }),
            'requester_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tvoj@email.com'
            }),
            'requester_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+421 123 456 789 (voliteľné)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Názov musí byť aspoň 5 znakov dlhý.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise forms.ValidationError('Popis musí byť aspoň 20 znakov dlhý.')
        return description


class RequestFilterForm(forms.Form):
    """Form for filtering requests in dashboard"""
    STATUS_CHOICES = [
        ('', '--- Všetky statusy ---'),
        ('open', '🟢 Otvorená'),
        ('in_review', '🟡 V preverovaní'),
        ('in_progress', '🟠 V riešení'),
        ('resolved', '✅ Vyriešená'),
        ('rejected', '❌ Zamietnutá'),
    ]

    PRIORITY_CHOICES = [
        ('', '--- Všetky priority ---'),
        ('low', '🔵 Nízka'),
        ('medium', '🟡 Stredná'),
        ('high', '🔴 Vysoká'),
        ('critical', '🔴🔴 Kritická'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='--- Všetky kategórie ---',
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Hľadať výraz...'
        })
    )


class RequestReviewForm(forms.ModelForm):
    """Form for admin to review and categorize requests"""

    class Meta:
        model = Request
        fields = [
            'title', 'description', 'category', 'priority',
            'value_score', 'review_notes', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'readonly': True,
                'rows': 5
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'value_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'type': 'range'
            }),
            'review_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tvoje poznámky k žiadosti...',
                'rows': 3
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
