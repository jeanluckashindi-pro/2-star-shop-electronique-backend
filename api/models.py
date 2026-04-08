from django.db import models


class Category(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # ex: cat_music
    label = models.CharField(max_length=100)
    icon_key = models.CharField(max_length=30, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.label


class Product(models.Model):
    BADGE_CHOICES = [
        ("Nouveau", "Nouveau"),
        ("Populaire", "Populaire"),
        ("Top", "Top"),
        ("Promo", "Promo"),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        related_name="products",
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    badge = models.CharField(max_length=10, choices=BADGE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"

    def __str__(self):
        return f"{self.name} - {self.email}"


class AdminUser(models.Model):
    email = models.EmailField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)  # bcrypt
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_users"

    def __str__(self):
        return self.email
