# Generated by Django 5.1.3 on 2024-12-31 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todolist', '0012_alter_additem_notification_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additem',
            name='notification_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='additem',
            name='notification_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
