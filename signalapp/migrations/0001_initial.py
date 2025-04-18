# Generated by Django 4.2.2 on 2023-06-22 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SignalCoin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('coin_id', models.CharField(max_length=256)),
                ('symbol', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ['created_at'],
                'abstract': False,
            },
        ),
    ]
