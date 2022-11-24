# Generated by Django 3.2.7 on 2022-11-23 14:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('press', '0008_alter_comment_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='publish_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cooluser',
            name='github_profile',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
