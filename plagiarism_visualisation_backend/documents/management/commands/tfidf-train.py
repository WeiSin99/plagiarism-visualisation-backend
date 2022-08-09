import os
import re
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from documents.models import Document
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Train tfidf model"

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

        eng_source_documents = Document.objects.filter(language="en").values_list(
            "doc_num", flat=True
        )

        all_eng_docs = []
        source_filenum = []
        suspicious_filenum = []

        # loop through the source directory
        for dirpath, _, files in os.walk(source_path):
            if dirpath == source_path:
                continue

            for file in files:
                if file == ".DS_Store" or file.endswith(".xml"):
                    continue

                filename, _ = os.path.splitext(os.path.basename(file))
                file_number = re.search(r"\d+", filename)
                file_number = file_number and int(file_number.group())

                if file_number in eng_source_documents:
                    source_filenum.append(file_number)
                    all_eng_docs.append(os.path.join(dirpath, file))

        tfidf_vectorizer = TfidfVectorizer(
            input="filename", smooth_idf=True, use_idf=True
        )
        tfidf_vector = tfidf_vectorizer.fit_transform(all_eng_docs)

        print("start writing")
        with open(
            os.path.join(
                curpath, "../../../../dataset-preprocessed/tfidf-model.pickle"
            ),
            "wb",
        ) as model_file:
            pickle.dump(tfidf_vectorizer, model_file)
        with open(
            os.path.join(
                curpath, "../../../../dataset-preprocessed/tfidf-vector.pickle"
            ),
            "wb",
        ) as vector_file:
            pickle.dump(tfidf_vector, vector_file)
        with open(
            os.path.join(
                curpath, "../../../../dataset-preprocessed/source-filenum.pickle"
            ),
            "wb",
        ) as source_file:
            pickle.dump(source_filenum, source_file)
