# Generated by Django 4.1 on 2022-08-06 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0013_givenplagiarismcase_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="givenplagiarismcase",
            name="obfuscation",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
