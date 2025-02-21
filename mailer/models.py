from django.db import models
from django.contrib.auth.models import User

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_preference")
    use_whatsapp = models.BooleanField(default=True)
    use_sms = models.BooleanField(default=False)
    use_email = models.BooleanField(default=True)
    use_push = models.BooleanField(default=True)  # Mobile app push notifications
    use_in_app = models.BooleanField(default=True)  # For showing notifications inside your web/app

    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Notification Preferences"


from django.db import models

class AmazonProduct(models.Model):
    product_name = models.CharField(max_length=500)
    product_price = models.CharField(max_length=50)
    product_MRP = models.CharField(max_length=50)
    product_img = models.URLField()
    product_rating = models.CharField(max_length=50)
    total_customer_rating = models.IntegerField()
    product_page_url = models.URLField()

    def __str__(self):
        return self.product_name

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    AVAILABILITY_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('coming_soon', 'Coming Soon'),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    # Categories and Brand
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='products')
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)]
    )
    
    # Stock and Availability
    stock_quantity = models.IntegerField(default=0)
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='in_stock'
    )
    
    # Media
    main_image = models.ImageField(upload_to='product_images/')
    
    # SEO and Search
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Additional Features
    features = models.JSONField(default=dict, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['brand']),
            models.Index(fields=['category']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.meta_title:
            self.meta_title = self.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        """Returns the current effective price (discount_price if available, otherwise regular price)"""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if discount price is set"""
        if self.discount_price and self.price:
            return round((1 - float(self.discount_price) / float(self.price)) * 100, 2)
        return 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"