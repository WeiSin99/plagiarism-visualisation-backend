# Generated by Django 4.1 on 2022-08-18 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0016_plagiarismcase_score"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="doc_num",
            field=models.IntegerField(db_index=True, unique=True),
        ),
        migrations.AlterField(
            model_name="suspiciousdocument",
            name="doc_num",
            field=models.IntegerField(db_index=True, unique=True),
        ),
    ]
