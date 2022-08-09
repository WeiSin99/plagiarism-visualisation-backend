import os
import re
import json
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import coo_matrix, vstack

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
        path = "../../../../dataset-preprocessed"
        suspicious_path = os.path.join(curpath, options["suspicious"])

        with open(
            os.path.join(curpath, path, "tfidf-model.pickle"), "rb"
        ) as model_file:
            tfidf_vectorizer = pickle.load(model_file)
        with open(
            os.path.join(curpath, path, "tfidf-vector.pickle"), "rb"
        ) as vector_file:
            tfidf_vector = pickle.load(vector_file)
        with open(
            os.path.join(curpath, path, "source-filenum.pickle"), "rb"
        ) as source_file:
            source_filenum = pickle.load(source_file)

        with open(
            os.path.join(curpath, path, "suspicious-references.json"), "r"
        ) as reference_f:
            true_sources = json.load(reference_f)

        results = {}
        # for threshold in range(1, 6):
        true_positives = 0
        total_predicted_positives = 0
        total_actual_positives = 0

        for dirpath, _, files in os.walk(suspicious_path):
            if dirpath == suspicious_path:
                continue

            for file in files:
                if file == ".DS_Store" or file.endswith(".xml"):
                    continue

                filename, _ = os.path.splitext(os.path.basename(file))
                file_number = re.search(r"\d+", filename)
                file_number = file_number and int(file_number.group())
                if not file_number:
                    file_number = -1

                if file_number > 10000:
                    continue

                if file_number % 1000 == 0:
                    print(file_number)

                suspicious_vector = tfidf_vectorizer.transform(
                    [os.path.join(dirpath, file)]
                )
                cosine_similarities = cosine_similarity(suspicious_vector, tfidf_vector)

                true_source = true_sources[str(file_number)]
                similarity = cosine_similarities[0]
                top_indices = np.argsort(similarity)[::-1]

                candidates = []
                for index in top_indices:
                    if similarity[index] > 0.15:
                        candidates.append(source_filenum[index])

                true_positives += len(set(candidates).intersection(set(true_source)))
                total_actual_positives += len(true_source)
                total_predicted_positives += len(candidates)

        recall = true_positives / total_actual_positives
        precision = true_positives / total_predicted_positives
        print(recall)
        print(precision)
        print("")

        results[15] = {}
        results[15]["recall"] = recall
        results[15]["precision"] = precision

        with open(os.path.join(curpath, path, "tfidf-results.json"), "w") as f:
            json.dump(results, f)
