from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from apps.core.services.storage import StorageError, generate_safe_path, get_storage_service

from .forms import (
    AccountPasswordChangeForm,
    EmailAuthenticationForm,
    ProfileForm,
    StudentRegistrationForm,
)


def register(request):
    if request.user.is_authenticated:
        return redirect("core:post_login_redirect")
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Welcome to Cyber Defend Africa Academy!")
            return redirect("core:post_login_redirect")
    else:
        form = StudentRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(0)
        return response


class AccountLogoutView(LogoutView):
    next_page = "core:home"


class AccountPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class AccountPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class AccountPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


@login_required
def password_change(request):
    if request.method == "POST":
        form = AccountPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been updated.")
            return redirect("accounts:profile")
    else:
        form = AccountPasswordChangeForm(request.user)
    return render(request, "accounts/password_change.html", {"form": form})


def _signed_avatar_url(user):
    """Private bucket — always regenerate, never cache; signed URLs expire."""
    if not user.avatar_path:
        return None
    try:
        return get_storage_service().signed_url("avatars", user.avatar_path)
    except StorageError:
        return None


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            avatar = form.cleaned_data.get("avatar")
            if avatar:
                old_avatar_path = user.avatar_path
                path = generate_safe_path("avatars", str(user.id), original_filename=avatar.name)
                try:
                    get_storage_service().upload("avatars", path, avatar, content_type=avatar.content_type)
                except StorageError as exc:
                    messages.error(request, f"Profile picture upload failed: {exc}")
                    return render(request, "accounts/profile.html", {
                        "form": form, "avatar_url": _signed_avatar_url(request.user),
                    })
                user.avatar_path = path
                if old_avatar_path:
                    try:
                        get_storage_service().delete("avatars", old_avatar_path)
                    except StorageError:
                        pass  # best-effort cleanup — the new avatar is already set
            user.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {
        "form": form, "avatar_url": _signed_avatar_url(request.user),
    })
