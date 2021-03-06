# Generated by Django 3.1.2 on 2020-10-25 15:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('discount_percent', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('total_stock', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='MeasurnmentUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_name', models.CharField(choices=[('ml', 'ml'), ('l', 'litre'), ('kg', 'kg'), ('g', 'grams'), ('units', 'units')], default='units', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placed_on', models.DateTimeField(auto_now_add=True)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ShopAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_manage_inventory', 'Can add/remove ingredients and view placed orders')],
            },
        ),
        migrations.CreateModel(
            name='ProductTypeIngredientRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty_of_ingredient_used', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_api.ingredient')),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_api.producttype')),
            ],
        ),
        migrations.AddField(
            model_name='producttype',
            name='ingredients_used',
            field=models.ManyToManyField(through='main_api.ProductTypeIngredientRelation', to='main_api.Ingredient'),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at_date', models.DateTimeField(auto_now_add=True)),
                ('use_before_date', models.DateTimeField()),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main_api.discount')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main_api.order')),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_api.producttype')),
            ],
        ),
        migrations.AddField(
            model_name='ingredient',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_api.measurnmentunit'),
        ),
        migrations.AddConstraint(
            model_name='producttypeingredientrelation',
            constraint=models.UniqueConstraint(fields=('product_type', 'ingredient'), name='product_ingredient_unique_pair'),
        ),
    ]
