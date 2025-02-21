
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from django_filters import rest_framework as filters
from django.db import models
from django.utils import timezone  # ✅ Add this at the top
from .models import Location, Category, Product, InventoryTransaction,Supplier,PurchaseOrder,ProductMovement
from .serializers import (
    LocationSerializer, CategorySerializer,
    ProductSerializer, InventoryTransactionSerializer,SupplierSerializer,PurchaseOrderSerializer,ProductMovementSerializer
)
from .filters import ProductFilter
from django.db.models import F, ExpressionWrapper, FloatField, Sum, Case, When, Value, IntegerField
from django.db.models.functions import ExtractYear, ExtractMonth


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    @action(detail=False, methods=['get'])
    def reorder_suggestions(self, request):
        """
        Retrieve products that need reordering (quantity below reorder point).
        """
        reorder_products = self.queryset.filter(quantity__lt=F('reorder_point'))

        data = reorder_products.values(
            'id', 'name', 'quantity', 'reorder_point'
        )

        return Response({'reorder_suggestions': list(data)})

    @action(detail=False, methods=['get'])
    def inventory_health(self, request):
        total_products = self.queryset.count()
        low_stock = self.queryset.filter(quantity__lte=F('reorder_point')).count()
        expired = self.queryset.filter(expiry_date__lt=timezone.now().date()).count()
        
        inventory_value = self.queryset.aggregate(
            total_value=Sum(F('quantity') * F('unit_price'))
        )['total_value'] or 0  # Avoid None value

        return Response({
            'total_products': total_products,
            'low_stock_percentage': (low_stock / total_products) * 100 if total_products > 0 else 0,
            'expired_percentage': (expired / total_products) * 100 if total_products > 0 else 0,
            'inventory_value': inventory_value
        })
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Retrieve products that are low in stock (quantity below reorder point).
        """
        low_stock_products = self.queryset.filter(quantity__lt=F('reorder_point'))

        data = low_stock_products.values(
            'id', 'name', 'quantity', 'reorder_point'
        )

        return Response({'low_stock_products': list(data)})




    @action(detail=False, methods=['get'])
    def age_analysis(self, request):
        today = timezone.now().date()

        # Exclude products where manufacture_date is NULL
        products = self.queryset.exclude(manufacture_date__isnull=True)

        # Annotate each product with calculated age in months
        products = products.annotate(
            age_in_months=((today.year - ExtractYear('manufacture_date')) * 12 + (today.month - ExtractMonth('manufacture_date')))
        )

        # Define age ranges
        age_ranges = [
            {'label': '0-3 months', 'min': 0, 'max': 3},
            {'label': '3-6 months', 'min': 3, 'max': 6},
            {'label': '6-12 months', 'min': 6, 'max': 12},
            {'label': 'Over 12 months', 'min': 12, 'max': None},
        ]

        cases = []
        for age_range in age_ranges:
            min_age = age_range['min']
            max_age = age_range['max']

            if max_age:
                cases.append(When(age_in_months__gte=min_age, age_in_months__lt=max_age, then=Value(age_range['label'])))
            else:
                cases.append(When(age_in_months__gte=min_age, then=Value(age_range['label'])))

        # Annotate products with age category
        products = products.annotate(age_category=Case(*cases, output_field=models.CharField()))

        analysis = {}
        for age_range in age_ranges:
            label = age_range['label']
            filtered_products = products.filter(age_category=label)

            total_value = filtered_products.aggregate(
                total_value=Sum(F('quantity') * F('unit_price'))
            )['total_value'] or 0  # Ensure no None values

            analysis[label] = {'count': filtered_products.count(), 'total_value': total_value}

        return Response(analysis)


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    filterset_fields = ['product', 'transaction_type', 'transaction_date']


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_fields = ['active', 'rating']

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['status', 'supplier', 'order_date']
    
    @action(detail=True, methods=['post'])
    def receive_items(self, request, pk=None):
        po = self.get_object()
        items_received = request.data.get('items', [])
        
        for item in items_received:
            po_item = po.items.get(id=item['id'])
            po_item.quantity_received = item['quantity_received']
            po_item.save()
            
            # Update inventory
            product = po_item.product
            product.quantity += item['quantity_received']
            product.save()
        
        po.status = 'RECEIVED'
        po.save()
        return Response({'status': 'Items received successfully'})

class ProductMovementViewSet(viewsets.ModelViewSet):
    queryset = ProductMovement.objects.all()
    serializer_class = ProductMovementSerializer
    
    def perform_create(self, serializer):
        movement = serializer.save()
        # Update quantities at both locations
        movement.from_location.products.filter(id=movement.product.id).update(
            quantity=models.F('quantity') - movement.quantity
        )
        movement.to_location.products.filter(id=movement.product.id).update(
            quantity=models.F('quantity') + movement.quantity
        )