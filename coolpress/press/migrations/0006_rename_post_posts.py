# Generated by Django 3.2.7 on 2022-11-14 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('press', '0005_auto_20221114_1253'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Post',
            new_name='Posts',
        ),
    ]