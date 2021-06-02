# Generated by Django 3.1.11 on 2021-06-01 21:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wagtailcore', '0052_pagelogentry'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('wagtailsearchpromotions', '0002_capitalizeverbose'),
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('test_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PageWitRichText',
            new_name='PageWithRichText',
        ),
    ]
