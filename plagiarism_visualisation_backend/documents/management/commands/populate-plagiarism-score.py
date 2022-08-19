import os
import json
import random

from documents.models import Document, SuspiciousDocument
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Preprocess source sentences"

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            type=str,
            choices=["source", "suspicious"],
            help="Type of documents to be preprocessed.",
        )

    def handle(self, *args, **options):
        if options["type"] == "source":
            doc_nums = Document.objects.all().values_list("doc_num", flat=True)
        else:
            doc_nums = SuspiciousDocument.objects.all().values_list(
                "doc_num", flat=True
            )

        for doc_num in doc_nums:
            print(doc_num)
            if options["type"] == "source":
                doc = Document.objects.get(doc_num=doc_num)
            else:
                doc = SuspiciousDocument.objects.get(doc_num=doc_num)

            plagiarised_sentences = []
            plagiarism_cases = doc.detected_plagiarism_cases().all()
            for plag_case in plagiarism_cases:
                if options["type"] == "source":
                    plagiarised_sentences.append(
                        list(
                            range(
                                plag_case.source_start_sentence,
                                plag_case.source_end_sentence + 1,
                            )
                        )
                    )
                else:
                    plagiarised_sentences.append(
                        list(
                            range(
                                plag_case.sus_start_sentence,
                                plag_case.sus_end_sentence + 1,
                            )
                        )
                    )

            plagiarised_sentences = [
                sentence
                for sentences in plagiarised_sentences
                for sentence in sentences
            ]
            plagiarised_sentences = list(set(plagiarised_sentences))

            plagiarised_part_length = sum(
                [
                    len(sentence.raw_text)
                    for sentence in doc.sentences.filter(
                        number__in=plagiarised_sentences
                    )
                ]
            )
            total_length = len(doc.raw_text)
            plagiarism_score = plagiarised_part_length / total_length
            doc.plagiarism_score = plagiarism_score
            doc.save()
