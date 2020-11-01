from datetime import datetime
from django.db.models import Sum, Count
from rest_framework import viewsets, mixins
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import IngredientSerializer, IngredientReadOnlySerializer, ProductTypeSerializer, ProductSerializer, \
    OrderSerializer, \
    DiscountSerializer, ProductTypeIngredientRelationSerializer
from .models import Ingredient, ProductType, Product, Order, Discount, ProductTypeIngredientRelation
from .permissions import IsShopAdminOrReadOnly, IsOrderOwner


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShopAdminOrReadOnly]


class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShopAdminOrReadOnly]


class ProductTypeIngredientRelationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ProductTypeIngredientRelation.objects.all()
    serializer_class = ProductTypeIngredientRelationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShopAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(use_before_date__gt=datetime.today()).annotate(total_items=Sum('product_type'))
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShopAdminOrReadOnly]

    @action(detail=False)
    def view_monthly_sales(self, request):
        qs = Product.objects.filter(order__isnull=False).all().annotate(
            sales=Count('product_type')).order_by('-sales')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrderOwner]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopAdminOrReadOnly]
