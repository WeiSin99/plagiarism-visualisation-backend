# Generated by Django 4.0.6 on 2022-08-02 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0007_alter_sentence_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentence',
            name='fasttext_vector',
        ),
    ]
