from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email address.')
        return email

class VerifyOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'autocomplete': 'off'
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise ValidationError('OTP must contain only digits.')
        return otp

class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)
        return self.cleaned_data

class TwoFactorAuthForm(forms.Form):
    method = forms.ChoiceField(
        choices=[
            ('email_otp', 'Email OTP'),
            ('authenticator', 'Authenticator App')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

class VerifyTwoFactorForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'autocomplete': 'off'
        })
    )
    backup_code = forms.CharField(
        max_length=8,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter backup code'
        })
    )

    def clean(self):
        otp = self.cleaned_data.get('otp')
        backup_code = self.cleaned_data.get('backup_code')

        if not otp and not backup_code:
            raise ValidationError('Please enter either OTP or backup code.')
        return self.cleaned_data
