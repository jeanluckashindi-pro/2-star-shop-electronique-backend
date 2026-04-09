from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, MessageViewSet
from .auth import AdminLoginView, AdminLogoutView, AdminRefreshView, AdminMeView, ForgotPasswordView, VerifyOTPView, ResetPasswordView

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("messages", MessageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("auth/logout/", AdminLogoutView.as_view(), name="admin-logout"),
    path("auth/refresh/", AdminRefreshView.as_view(), name="admin-refresh"),
    path("auth/me/", AdminMeView.as_view(), name="admin-me"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
