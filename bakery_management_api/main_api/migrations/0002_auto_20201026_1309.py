# Generated by Django 3.1.2 on 2020-10-26 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttype',
            name='ingredients_used',
            field=models.ManyToManyField(null=True, through='main_api.ProductTypeIngredientRelation', to='main_api.Ingredient'),
        ),
    ]
