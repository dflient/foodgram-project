# Generated by Django 4.2.8 on 2024-01-14 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingridient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=16, verbose_name='Единица измерения')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=5, verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Ингридиенты',
            },
        ),
    ]