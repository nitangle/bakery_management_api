from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.db.models.functions import Greatest


class Order(models.Model):
    placed_on = models.DateTimeField(auto_now_add=True)

    @property
    def order_amount(self):
        return self.product_set.aggregate(sum=models.Sum('selling_price')).get('sum')

    def __str__(self):
        return 'Order number {} placed by {}'.format(self.id,self.customer.username)


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(to=Order,on_delete=models.CASCADE)

    def get_full_name(self):
        user = ShopAdmin.objects.select_related('user').get(user=self.user)
        return user.first_name + ' ' + user.last_name

    def __repr__(self):
        user = ShopAdmin.objects.select_related('user').get(user=self.user)
        return 'full name {} {}'.format(user.first_name, user.last_name)

class ShopAdmin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_full_name(self):
        user = ShopAdmin.objects.select_related('user').get(user=self.user)
        return user.first_name + ' ' + user.last_name

    def __repr__(self):
        user = ShopAdmin.objects.select_related('user').get(user=self.user)
        return 'full name {} {}'.format(user.first_name, user.last_name)


class MeasurnmentUnit(models.Model):
    UNIT_CHOICES = (
        ('ml', 'ml'),
        ('l', 'litre'),
        ('kg', 'kg'),
        ('g', 'grams'),
        ('units', 'units'),
    )
    unit_name = models.CharField(max_length=5, choices=UNIT_CHOICES, default='units')

    def __str__(self):
        return self.unit_name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)
    unit = models.ForeignKey(to=MeasurnmentUnit, on_delete=models.CASCADE)
    total_stock = models.DecimalField(default=0, decimal_places=2, max_digits=10)

    def __str__(self):
        return self.name

    # def update_ingredient_stock(self, new_val):
    #     with transaction.atomic():
    #         try:
    #             original_stock = self.total_stock
    #             self.total_stock = new_val
    #             self.save()
    #         except IntegrityError:
    #             self.total_stock = original_stock
    #             self.save()

    def remove_ingredient(self, decrement=1):
        with transaction.atomic():
            try:
                original_stock = self.total_stock
                self.total_stock = Greatest(models.F('total_stock') - decrement,Decimal(0))
                self.save()
                self.refresh_from_db()

            except IntegrityError:
                self.total_stock = original_stock
                self.save()
                self.refresh_from_db()


class ProductType(models.Model):
    name = models.CharField(max_length=100)
    ingredients_used = models.ManyToManyField(Ingredient, through='ProductTypeIngredientRelation',blank=False,null=False)

    def __str__(self):
        return self.name

class ProductTypeIngredientRelation(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    qty_of_ingredient_used = models.DecimalField(decimal_places=2, max_digits=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product_type', 'ingredient'], name='product_ingredient_unique_pair')
        ]

    def display_ingredient_percentage(self):
        sum = ProductTypeIngredientRelation.objects.filter(product_type=self.product_type).aggregate(
            sum=models.Sum('qty_of_ingredient_used')).get('sum')
        return str((self.qty_of_ingredient_used / sum) * 100) + '%'



# optional for now
class Discount(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_percent = models.DecimalField(decimal_places=2, max_digits=10)


# treating each product as a unique entity
class Product(models.Model):
    created_at_date = models.DateTimeField(auto_now_add=True)
    use_before_date = models.DateTimeField()
    cost_price = models.DecimalField(decimal_places=2, max_digits=10)
    selling_price = models.DecimalField(decimal_places=2, max_digits=10)
    product_type = models.ForeignKey(to=ProductType, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True,blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True,blank=True)

    def save(self, *args, **kwargs):

        if self.discount:
            if self.discount.start_date <= timezone.now() and self.discount.end_date > timezone.now():
                self.selling_price = self.selling_price*(100 - self.discount.discount_percent)/100
        qs = ProductTypeIngredientRelation.objects.filter(product_type=self.product_type).select_related('ingredient')
        original_ingredient_list = []
        with transaction.atomic():
            try:
                for q in qs:
                    ingredient_to_be_updated = q.ingredient
                    qty_of_ingredient_used = q.qty_of_ingredient_used
                    total_ingredient_stock = ingredient_to_be_updated.total_stock
                    original_ingredient_list.append(total_ingredient_stock)
                    ingredient_to_be_updated.remove_ingredient(qty_of_ingredient_used)


            except IntegrityError:
                for q in qs:
                    ingredient_to_be_updated = q.ingredient
                    ingredient_to_be_updated.total_stock = original_ingredient_list.pop()

        super().save(*args, **kwargs)

# @receiver(pre_delete, sender=Product)
# def my_handler(sender, instance, using, **kwargs):
#     qs = ProductTypeIngredientRelation.objects.filter(product_type=instance.product_type).select_related('ingredient')
#     original_ingredient_list = []
#     with transaction.atomic():
#         try:
#             for q in qs:
#                 ingredient_to_be_updated = q.ingredient
#                 qty_of_ingredient_used = q.qty_of_ingredient_used
#                 total_ingredient_stock = ingredient_to_be_updated.total_stock
#                 original_ingredient_list.append(total_ingredient_stock)
#                 ingredient_to_be_updated.remove_ingredient(qty_of_ingredient_used)
#         except IntegrityError:
#             for q in qs:
#                 ingredient_to_be_updated = q.ingredient
#                 ingredient_to_be_updated.total_stock = original_ingredient_list.pop()
