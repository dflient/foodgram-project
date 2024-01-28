# Generated by Django 3.2.3 on 2024-01-28 12:32

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
                ('amount', models.FloatField(blank=True, null=True, verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Ингридиенты',
            },
        ),
    ]
