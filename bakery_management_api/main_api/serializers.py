from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ShopAdmin, MeasurnmentUnit, Ingredient, ProductType, Product, ProductTypeIngredientRelation, Order, \
    Discount
from django.db import transaction


class ShopAdminSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = ShopAdmin
        fields = ['username', 'email', 'full_name']
        read_only_fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    UNIT_CHOICES = (
        ('ml', 'ml'),
        ('l', 'litre'),
        ('kg', 'kg'),
        ('g', 'grams'),
        ('units', 'units'),
    )
    unit_name = serializers.ChoiceField(UNIT_CHOICES, write_only=True)

    class Meta:
        model = Ingredient
        # fields = '__all__'
        exclude = ['unit']
        # read_only_fields = ['name']

    def validate_total_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('stock of ingredient cannot be negative')
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        super.update(instance, validated_data)

    def create(self, validated_data):
        unit_name = validated_data.get('unit_name')
        name = validated_data.get('name')
        total_stock = validated_data.get('total_stock')
        obj = MeasurnmentUnit.objects.filter(unit_name=unit_name)
        print("hell")
        if not obj.exists():
            obj = MeasurnmentUnit.objects.create(unit_name=unit_name)
        else:
            obj = obj[0]
        ingredient = Ingredient.objects.create(name=name, total_stock=total_stock, unit=obj)
        return ingredient


class IngredientReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'unit']
        read_only_fields = ['unit']
        extra_kwargs = {
            'name': {'validators': []},
        }

    def create(self, validated_data):
        print("hey in read only ingredient create")
        name = validated_data.get('name')
        return Ingredient.objects.filter(name=name)[0]


class ProductTypeIngredientRelationSerializer(serializers.ModelSerializer):
    # product_type = ProductTypeSerializer(required=True)
    ingredient = IngredientReadOnlySerializer()
    ingredient_percent = serializers.CharField(source='display_ingredient_percentage', read_only=True)

    class Meta:
        model = ProductTypeIngredientRelation
        fields = ['ingredient', 'qty_of_ingredient_used', 'ingredient_percent']


class ProductTypeSerializer(serializers.ModelSerializer):
    ingredient_list = ProductTypeIngredientRelationSerializer(source='producttypeingredientrelation_set', many=True,
                                                              required=True)

    class Meta:
        model = ProductType
        fields = ['name', 'ingredient_list']

    def validate_ingredient_list(self, value):
        print("hey in validate_ingredient_list")
        for elm in value:
            qty_of_ingredient_used = elm.get('qty_of_ingredient_used')
            ingredient_name = elm.get('ingredient').get('name')
            obj = Ingredient.objects.filter(name=ingredient_name)
            print("yell")
            if obj.exists():
                if qty_of_ingredient_used > obj[0].total_stock:
                    raise serializers.ValidationError('Qty of ingredient cannot exceed total stock of ingredient')
            else:
                raise serializers.ValidationError('Ingredient does not exist. Please create the ingredient first.')

        return value

    def create(self, validated_data):
        name = validated_data.get('name')
        product_type_created = ProductType.objects.get_or_create(name=name)
        product_type_created = product_type_created[0]
        print('product type index-->{}'.format(product_type_created))
        ingredient_list = validated_data.pop('producttypeingredientrelation_set')
        for elm in ingredient_list:
            ingredient_name = elm.get('ingredient').get('name')
            qty_used = elm.get('qty_of_ingredient_used')
            if qty_used < 0:
                raise serializers.ValidationError('Quantity of ingredient to be used cannot be less than 0.')
            obj = Ingredient.objects.filter(name=ingredient_name)
            print("yell")
            if not obj.exists():
                raise serializers.ValidationError(
                    'Ingredient does not exist. Please create it first by going to appropriate url from apiroot.')
            elif qty_used > obj[0].total_stock:
                raise serializers.ValidationError(
                    'Quantity of ingredient to be used cannot be greater than its entire stock available.')
            else:
                obj = obj[0]
            ProductTypeIngredientRelation.objects.create(product_type=product_type_created, ingredient=obj,
                                                                   qty_of_ingredient_used=qty_used)
        return product_type_created

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        ingredient_list = validated_data.pop('producttypeingredientrelation_set')
        for elm in ingredient_list:
            ingredient_name = elm.get('ingredient').get('name')
            qty_used = elm.get('qty_of_ingredient_used')
            print("yell")
            if qty_used < 0:
                raise serializers.ValidationError('Quantity of ingredient to be used cannot be less than 0.')
            obj = Ingredient.objects.filter(name=ingredient_name)
            if not obj.exists():
                raise serializers.ValidationError(
                    'Ingredient does not exist. Please create it first by going to appropriate url from apiroot.')
            elif qty_used > obj[0].total_stock:
                raise serializers.ValidationError(
                    'Quantity of ingredient to be used cannot be greater than its entire stock available.')
            elif qty_used == 0:
                ProductTypeIngredientRelationSerializer.objects.filter(product_type=instance,
                                                                       ingredient=obj[0]).delete()
            else:
                pr = ProductTypeIngredientRelationSerializer.objects.filter(product_type=instance, ingredient=obj[0])
                pr.qty_used = qty_used
                pr.save()

        return instance


class ProductSerializer(serializers.ModelSerializer):
    product_type = serializers.CharField(source='product_type.name')

    # discount = serializers.CharField(source='product_type.name')

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at_date']

    def create(self, validated_data):
        product_type_data = validated_data.pop('product_type')
        print(product_type_data)
        product_type_obj = ProductType.objects.filter(name=product_type_data.get('name'))
        if not product_type_obj.exists():
            raise serializers.ValidationError('product type should already be created!')
        product_type_obj = product_type_obj[0]
        product = Product.objects.create(product_type=product_type_obj, **validated_data)
        return product

    def update(self, instance, validated_data):
        product_type_data = validated_data.pop('product_type', instance.product_type)
        product_type_obj = ProductType.objects.filter(name=product_type_data.get('name'))
        if not product_type_obj.exists():
            raise serializers.ValidationError('product type should already be created!')
        product_type_obj = product_type_obj[0]
        instance.product_type = product_type_obj
        super(self, instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    order_total = serializers.DecimalField(source='order_amount', max_digits=10, decimal_places=2, read_only=True)
    product_set = serializers.PrimaryKeyRelatedField(many=True,queryset=Product.objects.all())
    customer_set = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    class Meta:
        model = Order
        depth = 1
        fields = ['id','product_set', 'customer', 'placed_on', 'order_total']




class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        product_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
        depth = 1
        fields = ['product_set', 'start_date', 'end_date', 'discount_percent']
