from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view


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
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)