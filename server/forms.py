from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Request, Category, Expert


class RequestSubmissionForm(forms.ModelForm):
    """Form for submitting new help requests"""

    class Meta:
        model = Request
        fields = [
            'is_corporate', 'company_name', 'company_email', 'due_date',
            'title', 'description', 'requester_name', 'requester_email',
            'requester_phone', 'requester_type', 'category',
            'target_skills', 'required_languages', 'target_experience'
        ]
        widgets = {
            'is_corporate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'company_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'company@example.com'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Request title (e.g. Need experienced React developer)',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detailed request description...',
                'rows': 6
            }),
            'requester_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'requester_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'requester_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional phone'
            }),
            'requester_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'target_skills': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 8}),
            'required_languages': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 8}),
            'target_experience': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_skills'].queryset = self.fields['target_skills'].queryset.order_by('name')
        self.fields['required_languages'].queryset = self.fields['required_languages'].queryset.order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        is_corporate = cleaned_data.get('is_corporate')
        company_name = cleaned_data.get('company_name')
        company_email = cleaned_data.get('company_email')

        if is_corporate:
            if not company_name:
                self.add_error('company_name', 'Company name is required for corporate requests.')
            if not company_email:
                self.add_error('company_email', 'Company email is required for corporate requests.')

        if not cleaned_data.get('title'):
            self.add_error('title', 'Title is required.')

        if not cleaned_data.get('description'):
            self.add_error('description', 'Description is required.')

        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Názov musí byť aspoň 5 znakov dlhý.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError('Popis musí byť aspoň 10 znakov dlhý.')
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


class ExpertProfileForm(forms.ModelForm):
    """Form for editing expert profile"""

    class Meta:
        model = Expert
        fields = [
            'bio', 'skills', 'languages', 'work_experience', 'availability'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself, your background, and what you can help with...',
                'rows': 4
            }),
            'skills': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 8
            }),
            'languages': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 6
            }),
            'work_experience': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your relevant work experience and achievements...',
                'rows': 6
            }),
            'availability': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].queryset = self.fields['skills'].queryset.order_by('name')
        self.fields['languages'].queryset = self.fields['languages'].queryset.order_by('name')

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


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email address',
            'autocomplete': 'email',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already used by another account.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UsernameEmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Username/email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username/email',
            'autocomplete': 'username',
        }),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })

    def clean(self):
        identifier = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if identifier is not None and password:
            user_identifier = identifier
            if '@' in identifier:
                User = get_user_model()
                matched_user = User.objects.filter(email__iexact=identifier).first()
                if matched_user:
                    user_identifier = matched_user.get_username()

            self.user_cache = authenticate(
                self.request,
                username=user_identifier,
                password=password,
            )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
