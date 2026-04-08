from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, MessageViewSet
from .auth import AdminLoginView, AdminRefreshView, AdminMeView

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("messages", MessageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("auth/refresh/", AdminRefreshView.as_view(), name="admin-refresh"),
    path("auth/me/", AdminMeView.as_view(), name="admin-me"),
]
