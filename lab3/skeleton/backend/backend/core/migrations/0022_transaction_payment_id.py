# Generated by Django 5.1.1 on 2024-10-11 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_alter_offer_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_id',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
