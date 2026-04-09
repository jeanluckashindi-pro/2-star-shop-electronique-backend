from rest_framework import viewsets, parsers, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Message
from .serializers import CategorySerializer, ProductSerializer, MessageSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id", "label", "icon_key", "desc"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "badge", "category__id", "category__label"]
    filterset_fields = ["badge", "category"]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_serializer_context(self):
        return {"request": self.request}


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("-created_at")
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "email", "message"]
    filterset_fields = ["is_read", "is_pinned", "is_archived"]
