# inventory/serializers.py
from rest_framework import serializers
from .models import Location, Category, Product, InventoryTransaction,Supplier,PurchaseOrderItem,PurchaseOrder,QualityCheck,InventoryAdjustment,ProductMovement

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    age_in_months = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class QualityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityCheck
        fields = '__all__'

class InventoryAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAdjustment
        fields = '__all__'

class ProductMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMovement
        fields = '__all__'