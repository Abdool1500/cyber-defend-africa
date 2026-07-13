from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm

from apps.core.forms import BootstrapFormMixin

from .models import User


class AdminUserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email", "full_name", "role")


class AdminUserChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = "__all__"


class StudentRegistrationForm(BootstrapFormMixin, forms.ModelForm):
    """Public self-registration. Always creates a student — role is never
    exposed as a field here, so nobody can register as instructor/admin."""

    first_name = forms.CharField(label="First Name", max_length=75)
    last_name = forms.CharField(label="Last Name", max_length=75)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput, min_length=8)
    agree_terms = forms.BooleanField(
        label="I agree to the Terms of Service",
        required=True,
        error_messages={"required": "You must agree to the Terms of Service to create an account."},
    )

    field_order = [
        "first_name", "last_name", "email", "phone", "country",
        "password1", "password2", "agree_terms",
    ]

    class Meta:
        model = User
        fields = ["email", "phone", "country"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = True
        self.fields["country"].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        first_name = self.cleaned_data["first_name"].strip()
        last_name = self.cleaned_data["last_name"].strip()
        user.full_name = f"{first_name} {last_name}".strip()
        user.role = User.Role.STUDENT
        user.status = User.Status.ACTIVE
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(label="Email")
    remember_me = forms.BooleanField(label="Remember me", required=False, initial=True)


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "phone", "country", "bio"]


class AccountPasswordChangeForm(BootstrapFormMixin, forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    new_password2 = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Your current password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "Passwords do not match.")
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save(update_fields=["password"])
        return self.user
