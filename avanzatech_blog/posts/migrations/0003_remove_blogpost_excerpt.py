# Generated by Django 5.1.3 on 2024-12-06 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_remove_blogpost_coments_blogpost_comments_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='excerpt',
        ),
    ]