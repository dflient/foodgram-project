# Generated by Django 3.2.3 on 2024-01-29 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='Название')),
                ('color', models.CharField(max_length=16, verbose_name='Цветовой код')),
                ('slug', models.SlugField(unique=True, verbose_name='Уникальное имя')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
    ]
