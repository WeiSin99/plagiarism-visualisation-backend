# Generated by Django 4.1 on 2022-08-06 01:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0011_document_keywords_suspiciousdocument_keywords"),
    ]

    operations = [
        migrations.CreateModel(
            name="GivenPlagiarismCase",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sus_start_sentence", models.IntegerField()),
                ("sus_end_sentence", models.IntegerField()),
                ("sus_length", models.IntegerField()),
                ("sus_word_len", models.IntegerField()),
                ("source_start_sentence", models.IntegerField()),
                ("source_end_sentence", models.IntegerField()),
                ("source_length", models.IntegerField()),
                ("source_word_len", models.IntegerField()),
                ("obfuscation", models.CharField(max_length=15)),
                (
                    "source_document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="given_plagiarism_cases",
                        to="documents.document",
                    ),
                ),
                (
                    "sus_document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="given_plagiarism_cases",
                        to="documents.suspiciousdocument",
                    ),
                ),
            ],
        ),
    ]
