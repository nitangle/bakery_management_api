from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'ingredient',views.IngredientViewSet)
router.register(r'product_type',views.ProductTypeViewSet)
router.register(r'product_ingredient_relation',views.ProductTypeIngredientRelationViewSet)
router.register(r'product',views.ProductViewSet)
router.register(r'order',views.OrderViewSet)
router.register(r'discounts',views.DiscountViewSet)

urlpatterns = [
    path('',include(router.urls)),
]