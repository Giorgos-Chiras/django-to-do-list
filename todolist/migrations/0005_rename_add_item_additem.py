# Generated by Django 5.1.3 on 2024-11-13 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todolist', '0004_rename_add_items_add_item'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='add_item',
            new_name='AddItem',
        ),
    ]
