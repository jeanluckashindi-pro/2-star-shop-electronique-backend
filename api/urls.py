from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from .views import CategoryViewSet, ProductViewSet, MessageViewSet
from .auth import AdminLoginView, AdminLogoutView, AdminRefreshView, AdminMeView, ForgotPasswordView, VerifyOTPView, ResetPasswordView

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("messages", MessageViewSet)


@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "categories": reverse("category-list", request=request, format=format),
        "products": reverse("product-list", request=request, format=format),
        "messages": reverse("message-list", request=request, format=format),
        "auth-login": request.build_absolute_uri("/api/auth/login/"),
        "auth-logout": request.build_absolute_uri("/api/auth/logout/"),
        "auth-refresh": request.build_absolute_uri("/api/auth/refresh/"),
        "auth-me": request.build_absolute_uri("/api/auth/me/"),
        "auth-forgot-password": request.build_absolute_uri("/api/auth/forgot-password/"),
        "auth-verify-otp": request.build_absolute_uri("/api/auth/verify-otp/"),
        "auth-reset-password": request.build_absolute_uri("/api/auth/reset-password/"),
    })


urlpatterns = [
    path("", api_root, name="api-root"),
    path("", include(router.urls)),
    path("auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("auth/logout/", AdminLogoutView.as_view(), name="admin-logout"),
    path("auth/refresh/", AdminRefreshView.as_view(), name="admin-refresh"),
    path("auth/me/", AdminMeView.as_view(), name="admin-me"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
