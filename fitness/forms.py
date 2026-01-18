from django import forms
from django.contrib.auth.models import User
from .models import Profile, Review

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'auth-input'
        }),
        label="Password"
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'eg. onege',
            'class': 'auth-input' # добавил класс для стиля
        }),
        label="Username"
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'eg. oneg@example.com',
            'class': 'auth-input' # добавил класс для стиля
        }),
        label="Email Address"
    )

    # ИСПРАВЛЕНО: используем Profile.Role.choices вместо ROLE_CHOICES
    role = forms.ChoiceField(
        choices=Profile.Role.choices,
        widget=forms.Select(attrs={
            'class': 'auth-input', # чтобы выпадающий список выглядел как инпуты
            'style': 'background-color: #111; color: white;' # на случай если в CSS нет стилей для select
        }),
        label="Select Your Role"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Профиль создается сигналом в models.py
            # Мы получаем его и обновляем выбранную роль
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.save()
        return user

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'height', 'weight', 'phone']
        widgets = {
            'height': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'cm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'kg'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7...'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input-file'}),
        }

