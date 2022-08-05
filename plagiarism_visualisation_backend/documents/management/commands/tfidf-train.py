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
        # source_path = os.path.join(curpath, options["source"])
        # suspicious_path = os.path.join(curpath, options["suspicious"])
        #
        # eng_source_documents = Document.objects.filter(language="en").values_list(
        #     "doc_num", flat=True
        # )
        #
        # all_eng_docs = []
        # source_filenum = []
        # suspicious_filenum = []
        #
        # # loop through the source directory
        # for dirpath, _, files in os.walk(source_path):
        #     if dirpath == source_path:
        #         continue
        #
        #     for file in files:
        #         if file == ".DS_Store" or file.endswith(".xml"):
        #             continue
        #
        #         filename, _ = os.path.splitext(os.path.basename(file))
        #         file_number = re.search(r"\d+", filename)
        #         file_number = file_number and int(file_number.group())
        #
        #         if file_number in eng_source_documents:
        #             source_filenum.append(file_number)
        #             all_eng_docs.append(os.path.join(dirpath, file))
        #
        # # loop through the suspicious directory
        # for dirpath, _, files in os.walk(suspicious_path):
        #     if dirpath == source_path:
        #         continue
        #
        #     for file in files:
        #         if file == ".DS_Store" or file.endswith(".xml"):
        #             continue
        #
        #         filename, _ = os.path.splitext(os.path.basename(file))
        #         file_number = re.search(r"\d+", filename)
        #         file_number = file_number and int(file_number.group())
        #
        #         suspicious_filenum.append(file_number)
        #         all_eng_docs.append(os.path.join(dirpath, file))
        #
        # tfidf_vectorizer = TfidfVectorizer(
        #     input="filename", smooth_idf=True, use_idf=True
        # )
        # tfidf_vector = tfidf_vectorizer.fit_transform(all_eng_docs)
        #
        # print("start writing")
        # with open(os.path.join(curpath, "tfidf-model.pickle"), "wb") as model_file:
        #     pickle.dump(tfidf_vectorizer, model_file)
        # with open(os.path.join(curpath, "tfidf-vector.pickle"), "wb") as vector_file:
        #     pickle.dump(tfidf_vector, vector_file)
        # with open(os.path.join(curpath, "source-filenum.pickle"), "wb") as source_file:
        #     pickle.dump(source_filenum, source_file)
        # with open(
        #     os.path.join(curpath, "suspicious-filenum.pickle"), "wb"
        # ) as suspicious_file:
        #     pickle.dump(suspicious_filenum, suspicious_file)

        # with open(os.path.join(curpath, "tfidf-model.pickle"), "rb") as model_file:
        #     tfidf_vectorizer = pickle.load(model_file)
        # with open(os.path.join(curpath, "tfidf-vector.pickle"), "rb") as vector_file:
        #     tfidf_vector = pickle.load(vector_file)
        with open(os.path.join(curpath, "source-filenum.pickle"), "rb") as source_file:
            source_filenum = pickle.load(source_file)
        with open(
            os.path.join(curpath, "suspicious-filenum.pickle"), "rb"
        ) as suspicious_file:
            suspicious_filenum = pickle.load(suspicious_file)
        #
        # # vector = tfidf_vectorizer.transform(
        # #     [
        # #         os.path.join(
        # #             curpath,
        # #             "../../../../dataset-preprocessed/suspicious-document/part22/suspicious-document10727.txt",
        # #         )
        # #     ]
        # # )
        #
        # source_tfidf = tfidf_vector[0:10419, :]
        # suspicious_tfidf = tfidf_vector[10419:, :]
        #
        # cosine_similarities = cosine_similarity(suspicious_tfidf, source_tfidf)
        # with open(
        #     os.path.join(curpath, "cosine-similarites.pickle"), "wb"
        # ) as cosine_file:
        #     pickle.dump(cosine_similarities, cosine_file)

        with open(
            os.path.join(curpath, "cosine-similarites.pickle"), "rb"
        ) as cosine_file:
            cosine_similarities = pickle.load(cosine_file)

        print(suspicious_filenum[10308])
        similarity = cosine_similarities[10308]
        top_indices = np.argsort(similarity)[::-1][:50]
        top_documents = [similarity[index] for index in top_indices]
        print(top_documents)
