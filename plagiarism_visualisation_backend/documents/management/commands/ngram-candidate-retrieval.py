import os
import re
import pickle
from nltk import ngrams

from documents.models import Document
from django.core.management.base import BaseCommand


def jaacard_similarity(ngram1, ngram2):
    set_x = set(ngram1)
    set_y = set(ngram2)
    intersection = set_x.intersection(set_y)
    union = set_x.union(set_y)

    if len(union) <= 0:
        return 0

    return len(intersection) / len(union)


class Command(BaseCommand):
    help = "Preprocess source sentences"

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="../../../../dataset-preprocessed/source-document",
            help="Path to source documents",
        )
        parser.add_argument(
            "-u",
            "--suspicious",
            type=str,
            default="../../../../dataset-preprocessed/suspicious-document",
            help="Path to source documents",
        )

    def handle(self, *args, **options):
        curpath = os.path.dirname(__file__)
        source_path = os.path.join(curpath, options["source"])
        suspicious_path = os.path.join(curpath, options["suspicious"])

        eng_source_documents = Document.objects.filter(language="en").values_list(
            "doc_num", flat=True
        )

        source_ngrams = []
        source_filenums = []
        # loop through the directory
        for dirpath, _, files in os.walk(source_path):
            if dirpath == source_path:
                continue

            for file in files:
                if file == ".DS_Store" or file.endswith(".xml"):
                    continue

                filename, _ = os.path.splitext(os.path.basename(file))
                file_number = re.search(r"\d+", filename)
                file_number = file_number and int(file_number.group())

                if file_number not in eng_source_documents:
                    continue

                if file_number not in [5984, 10403, 9191, 8169, 6165, 4987, 10108, 5]:
                    continue

                with open(os.path.join(dirpath, f"{filename}.txt")) as f:
                    text = f.read().split()

                source_filenums.append(file_number)
                source_ngrams.append(ngrams(text, 2))

        suspicious_ngrams = []
        suspicious_filenums = []
        # loop through suspicious directory
        for dirpath, _, files in os.walk(suspicious_path):
            if dirpath == source_path:
                continue

            for file in files:
                if file == ".DS_Store" or file.endswith(".xml"):
                    continue

                filename, _ = os.path.splitext(os.path.basename(file))
                file_number = re.search(r"\d+", filename)
                file_number = file_number and int(file_number.group())
                if file_number != 2871:
                    continue

                with open(os.path.join(dirpath, f"{filename}.txt")) as f:
                    text = f.read().split()

                suspicious_filenums.append(file_number)
                suspicious_ngrams.append(ngrams(text, 2))

        print(list(suspicious_ngrams[0]))
        for suspicious_ngram in suspicious_ngrams:
            for source_ngram in source_ngrams:
                print(jaacard_similarity(list(suspicious_ngram), list(source_ngram)))
