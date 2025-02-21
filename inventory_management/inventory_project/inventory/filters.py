# inventory/filters.py

from django_filters import rest_framework as filters
from django.db import models
from .models import PurchaseOrder, Product
from django.utils import timezone

# Your existing ProductFilter remains unchanged
class ProductFilter(filters.FilterSet):
    min_age = filters.NumberFilter(method='filter_min_age')
    max_age = filters.NumberFilter(method='filter_max_age')
    location = filters.CharFilter(field_name='location__name', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    min_quantity = filters.NumberFilter(field_name='quantity', lookup_expr='gte')
    max_quantity = filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    search = filters.CharFilter(method='filter_search')

    def filter_min_age(self, queryset, name, value):
        today = timezone.now().date()
        filtered_products = [p.id for p in queryset if (today.year - p.manufacture_date.year) * 12 + (today.month - p.manufacture_date.month) >= value]
        return queryset.filter(id__in=filtered_products)

    def filter_max_age(self, queryset, name, value):
        today = timezone.now().date()
        filtered_products = [p.id for p in queryset if (today.year - p.manufacture_date.year) * 12 + (today.month - p.manufacture_date.month) <= value]
        return queryset.filter(id__in=filtered_products)

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(sku__icontains=value) |
            models.Q(description__icontains=value)
        )

    class Meta:
        model = Product
        fields = ['location', 'category', 'min_quantity', 'max_quantity', 'min_age', 'max_age']

# New PurchaseOrderFilter
class PurchaseOrderFilter(filters.FilterSet):
    # Date range filters
    order_date_start = filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_end = filters.DateFilter(field_name='order_date', lookup_expr='lte')
    expected_delivery_start = filters.DateFilter(field_name='expected_delivery_date', lookup_expr='gte')
    expected_delivery_end = filters.DateFilter(field_name='expected_delivery_date', lookup_expr='lte')
    
    # Amount range filter
    min_total_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_total_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    # Supplier filters
    supplier_name = filters.CharFilter(field_name='supplier__name', lookup_expr='icontains')
    supplier_id = filters.NumberFilter(field_name='supplier__id')
    
    # Status filter
    status = filters.ChoiceFilter(choices=PurchaseOrder.STATUS_CHOICES, field_name='status')
    
    # PO number search
    po_number = filters.CharFilter(lookup_expr='icontains')
    
    # Custom search filter
    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(po_number__icontains=value) |
            models.Q(supplier__name__icontains=value) |
            models.Q(notes__icontains=value)
        )

    class Meta:
        model = PurchaseOrder
        fields = [
            'status', 'supplier_id',
            'order_date_start', 'order_date_end',
            'expected_delivery_start', 'expected_delivery_end',
            'min_total_amount', 'max_total_amount',
            'po_number'
        ]  # **Fixed the incorrect list definition**
