# Generated by Django 3.2.4 on 2021-06-04 13:04

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0062_comment_models_and_pagesubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageWithRichText',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('test_textfield', models.TextField(blank=True)),
                ('test_richtextfield', wagtail.core.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='PageWithStreamField',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('test_streamfield', wagtail.core.fields.StreamField([('char_block', wagtail.core.blocks.CharBlock(max_length=255)), ('boolean_block', wagtail.core.blocks.BooleanBlock()), ('text_block', wagtail.core.blocks.TextBlock()), ('email_block', wagtail.core.blocks.EmailBlock()), ('url_block', wagtail.core.blocks.URLBlock()), ('rich_text_block', wagtail.core.blocks.RichTextBlock()), ('raw_html_block', wagtail.core.blocks.RawHTMLBlock()), ('blockquote_block', wagtail.core.blocks.BlockQuoteBlock()), ('struct_block', wagtail.core.blocks.StructBlock([('field_a', wagtail.core.blocks.TextBlock()), ('field_b', wagtail.core.blocks.TextBlock())])), ('rich_text_struct_block', wagtail.core.blocks.StructBlock([('field_a', wagtail.core.blocks.RichTextBlock()), ('field_b', wagtail.core.blocks.RichTextBlock())])), ('nested_struct_block', wagtail.core.blocks.StructBlock([('child', wagtail.core.blocks.StructBlock([('field_a', wagtail.core.blocks.TextBlock()), ('field_b', wagtail.core.blocks.TextBlock())]))])), ('list_block', wagtail.core.blocks.ListBlock(wagtail.core.blocks.TextBlock())), ('list_block_with_struct_block', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('field_a', wagtail.core.blocks.TextBlock()), ('field_b', wagtail.core.blocks.TextBlock())]))), ('stream_block', wagtail.core.blocks.StreamBlock([('char_block', wagtail.core.blocks.CharBlock(max_length=255))])), ('nested_streamblock', wagtail.core.blocks.StreamBlock([('child', wagtail.core.blocks.StreamBlock([('char_block', wagtail.core.blocks.CharBlock(max_length=255))]))])), ('stream_block_with_struct_block', wagtail.core.blocks.StreamBlock([('child', wagtail.core.blocks.StructBlock([('field_a', wagtail.core.blocks.TextBlock()), ('field_b', wagtail.core.blocks.TextBlock())]))])), ('document_block', wagtail.documents.blocks.DocumentChooserBlock())], blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
