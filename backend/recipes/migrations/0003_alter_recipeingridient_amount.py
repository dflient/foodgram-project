# Generated by Django 4.2.8 on 2024-01-17 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_recipe_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingridient',
            name='amount',
            field=models.FloatField(verbose_name='Количество'),
        ),
    ]
