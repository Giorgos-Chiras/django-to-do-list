# Generated by Django 5.1.3 on 2024-12-31 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todolist', '0020_alter_additem_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additem',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='media/media'),
        ),
    ]