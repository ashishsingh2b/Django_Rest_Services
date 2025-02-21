# inventory/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'locations', views.LocationViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'transactions', views.InventoryTransactionViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'purchase-orders', views.PurchaseOrderViewSet)
router.register(r'product-movements', views.ProductMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]