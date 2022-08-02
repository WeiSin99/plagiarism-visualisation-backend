# Generated by Django 4.0.6 on 2022-08-02 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_remove_suspicioussentence_fasttext_vector'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='type',
        ),
        migrations.AddField(
            model_name='document',
            name='authors',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='suspiciousdocument',
            name='authors',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Author',
        ),
    ]
