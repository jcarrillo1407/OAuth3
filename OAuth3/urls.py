from django.urls import path
from .views import (
    RegisterView, LoginView, VerifyMFAView,
    ForgotPasswordView, ResetPasswordView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("verify-mfa/", VerifyMFAView.as_view(), name="verify-mfa"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]