import os
import json
import random

from documents.models import Document, SuspiciousDocument
from django.core.management.base import BaseCommand


def probability_generator(p):
    return random.random() <= p


def all_plagiarised_document(exclude_list):
    suspicious_documents = (
        SuspiciousDocument.objects.exclude(doc_num__in=exclude_list)
        .filter(language="en", doc_num__lte=10000)
        .values_list("doc_num", flat=True)
    )

    plagiarised_documents = []
    for doc_num in suspicious_documents:
        sus_doc = SuspiciousDocument.objects.get(doc_num=doc_num)
        if sus_doc.given_plagiarism_cases.count() > 0:
            plagiarised_documents.append(doc_num)

    return plagiarised_documents


def all_unplagiarised_documents(exclude_list):
    return (
        SuspiciousDocument.objects.exclude(doc_num__in=exclude_list)
        .filter(language="en", doc_num__lte=10000)
        .values_list("doc_num", flat=True)
    )


def get_document(all_docs, already_included_doc):
    if len(set(all_docs).intersection(set(already_included_doc))) == len(all_docs):
        return -1

    plagiarised_document = random.choice(all_docs)
    while plagiarised_document in already_included_doc:
        plagiarised_document = random.choice(all_docs)
    return plagiarised_document


class Command(BaseCommand):
    help = "Preprocess source sentences"

    def add_arguments(self, parser):
        parser.add_argument(
            "num",
            type=int,
            help="Number of corpora.",
        )
        parser.add_argument(
            "size",
            type=int,
            help="Size of each corpus.",
        )
        parser.add_argument(
            "alpha",
            type=float,
            help="Probability of a document is plagiarised.",
        )
        parser.add_argument(
            "beta",
            type=float,
            help="Probability of a document is plagiarised.",
        )

    def handle(self, *args, **options):
        plagiarised_documents = all_plagiarised_document([])
        not_plagiarised_documents = all_unplagiarised_documents(plagiarised_documents)

        source_documents = []
        suspicious_documents = []
        while len(source_documents) + len(suspicious_documents) < options["size"]:
            if probability_generator(options["alpha"]):
                # get plagiarised_documents
                suspicious_document = get_document(
                    plagiarised_documents, suspicious_documents
                )
                suspicious_documents.append(suspicious_document)

                sus_doc = SuspiciousDocument.objects.get(doc_num=suspicious_document)
                all_sources = sus_doc.given_plagiarised_source_document()

                while True:
                    # get one of its source
                    source_document = get_document(all_sources, source_documents)
                    if source_document < 0:
                        break

                    source_documents.append(source_document)
                    source_doc = Document.objects.get(doc_num=source_document)
                    all_sus = source_doc.given_plagiarised_suspicious_document()

                    while probability_generator(options["beta"]):
                        # get another plagiarised suspicious document that copy from the source if there is
                        other_sus_document = get_document(all_sus, suspicious_documents)
                        if other_sus_document < 0:
                            break

                        suspicious_documents.append(other_sus_document)

                    if not probability_generator(options["beta"]):
                        break
            else:
                # get suspicious document that is not plagiarised
                suspicious_document = get_document(
                    not_plagiarised_documents, suspicious_documents
                )
                suspicious_documents.append(suspicious_document)

        curpath = os.path.dirname(__file__)
        path = "../../../../dataset-preprocessed"
        with open(os.path.join(curpath, path, "corpus2.json"), "w") as f:
            json.dump(
                {
                    "source_documents": source_documents,
                    "suspicious_documents": suspicious_documents,
                },
                f,
            )
