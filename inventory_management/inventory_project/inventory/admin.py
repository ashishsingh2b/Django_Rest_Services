from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Supplier, Location, Category, PurchaseOrder, Product, 
    InventoryTransaction, PurchaseOrderItem, QualityCheck, 
    InventoryAdjustment, ProductMovement
)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'rating', 'active')
    search_fields = ('name', 'email', 'contact_person')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'status', 'order_date', 'expected_delivery_date', 'total_amount')
    list_filter = ('status', 'supplier')
    search_fields = ('po_number',)
    date_hierarchy = 'order_date'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'barcode_preview', 'qr_code_preview')

    def barcode_preview(self, obj):
        if obj.barcode:
            return mark_safe(f'<img src="{obj.barcode.url}" width="100"/>')
        return "No Barcode"

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="100"/>')
        return "No QR Code"

    barcode_preview.short_description = "Barcode"
    qr_code_preview.short_description = "QR Code"
@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'transaction_date')
    list_filter = ('transaction_type',)
    search_fields = ('product__name',)

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'product', 'quantity_ordered', 'quantity_received', 'unit_price')
    list_filter = ('purchase_order',)

@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch_number', 'check_date', 'inspector', 'result')
    list_filter = ('result',)
    search_fields = ('batch_number', 'product__name')

@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'adjustment_date', 'quantity_changed', 'reason', 'approved_by')
    list_filter = ('reason',)
    search_fields = ('product__name', 'approved_by')

@admin.register(ProductMovement)
class ProductMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'from_location', 'to_location', 'quantity', 'movement_date')
    list_filter = ('from_location', 'to_location')
    search_fields = ('product__name',)
