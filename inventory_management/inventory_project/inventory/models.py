# inventory/models.py
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import now
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from barcode import Code128
from barcode.writer import ImageWriter




class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('ORDERED', 'Ordered'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled')
    )

    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Ensure this exists
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    order_date = models.DateField(default=timezone.now)  # Ensure this exists
    expected_delivery_date = models.DateTimeField(default=now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.po_number

from django.db import models
from django.utils import timezone
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)  # SKU will be used for barcode & QR generation
    description = models.TextField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True)
    manufacture_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    
    # ✅ Fix: Added reorder_point field
    reorder_point = models.IntegerField(default=10)  # You can adjust the default value

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def generate_barcode(self):
        """Generate a barcode for the SKU"""
        barcode_image = Code128(self.sku, writer=ImageWriter())
        buffer = BytesIO()
        barcode_image.write(buffer)
        self.barcode.save(f"{self.sku}_barcode.png", ContentFile(buffer.getvalue()), save=False)

    def generate_qr_code(self):
        """Generate a QR code for the SKU"""
        qr = qrcode.make(f"Product: {self.name}\nSKU: {self.sku}\nPrice: {self.unit_price}")
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"{self.sku}_qrcode.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Override save method to generate barcode and QR code before saving"""
        if not self.barcode:
            self.generate_barcode()
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    @property
    def days_until_stockout(self):
        if hasattr(self, 'average_daily_usage') and self.average_daily_usage > 0:
            return self.quantity / self.average_daily_usage
        return None
    
    @property
    def should_reorder(self):
        return self.quantity <= self.reorder_point
    
    @property
    def age_in_months(self):
        if self.manufacture_date:
            today = timezone.now().date()
            age = (today.year - self.manufacture_date.year) * 12 + (today.month - self.manufacture_date.month)
            return age
        return 0

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if self.transaction_type == 'IN':
            self.product.quantity += self.quantity
        elif self.transaction_type == 'OUT':
            self.product.quantity -= self.quantity
        self.product.save()
        super().save(*args, **kwargs)







class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_price(self):
        return self.quantity_ordered * self.unit_price

class QualityCheck(models.Model):
    RESULT_CHOICES = (
        ('PASS', 'Passed'),
        ('FAIL', 'Failed'),
        ('PENDING', 'Pending Review')
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=50)
    check_date = models.DateTimeField(auto_now_add=True)
    inspector = models.CharField(max_length=100)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    notes = models.TextField(blank=True)
    
class InventoryAdjustment(models.Model):
    REASON_CHOICES = (
        ('DAMAGE', 'Damaged Goods'),
        ('EXPIRY', 'Expired Products'),
        ('THEFT', 'Theft/Loss'),
        ('COUNT', 'Count Adjustment'),
        ('OTHER', 'Other')
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    adjustment_date = models.DateTimeField(auto_now_add=True)
    quantity_changed = models.IntegerField()  # Can be negative for reductions
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField()
    approved_by = models.CharField(max_length=100)

class ProductMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    from_location = models.ForeignKey(Location, related_name='movements_from', on_delete=models.CASCADE)
    to_location = models.ForeignKey(Location, related_name='movements_to', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    movement_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
