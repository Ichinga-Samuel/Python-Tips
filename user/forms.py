from django import forms
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, \
    SetPasswordForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import Profile, User

attrs = {'class': 'form-control', 'placeholder': '', 'required': True}
User = get_user_model()


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={**attrs, **{'placeholder': 'Enter Email'}}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={**attrs, **{'placeholder': 'Enter Password'}}))

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password"
            " Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_active:
            raise ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


class UserRegistrationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': 'The two password fields didn’t match.',
    }
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address.',
                             widget=forms.EmailInput(attrs=attrs))
    name = forms.CharField(max_length=254, help_text='Enter Your Full Name.',
                            widget=forms.TextInput(attrs=attrs))
    password1 = forms.CharField(help_text='Your password must be 8-20 characters long, and must contain'
                                          ' numeric, lower and upper case letters',
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}))
    password2 = forms.CharField(help_text="Enter the same password as before, for verification.",
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}))

    class Meta:
        model = User
        fields = ['email', 'name', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserEditForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'name', 'password', 'is_active', 'is_admin')


class PasswordReset(PasswordResetForm):
    email = forms.EmailField(max_length=254, help_text='Enter the email address you registered with.',
                             widget=forms.EmailInput(attrs=attrs))


class PasswordChange(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs=attrs),
    )


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True, **attrs}),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["verified"]
        widgets = {"username": forms.TextInput(attrs=attrs)}
