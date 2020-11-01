from django.contrib import admin

from .models import Ingredient, ProductType, Product, ProductTypeIngredientRelation, Order, Discount, ShopAdmin, \
    MeasurnmentUnit


class ProductTypeIngredientRelationInline(admin.TabularInline):
    model = ProductTypeIngredientRelation
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    inlines = (ProductTypeIngredientRelationInline,)


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = (ProductTypeIngredientRelationInline,)
    # pass


class ProductAdmin(admin.ModelAdmin):
    pass


class ProductTypeIngredientRelationAdmin(admin.ModelAdmin):
    pass


class OrderAdmin(admin.ModelAdmin):
    pass


class DiscountAdmin(admin.ModelAdmin):
    pass


class MeasurnmentUnitAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductTypeIngredientRelation, ProductTypeIngredientRelationAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(MeasurnmentUnit, MeasurnmentUnitAdmin)
