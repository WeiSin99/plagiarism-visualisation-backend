import os
import re
import json
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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
        actual_positives = 0

        true_positives_500 = 0
        predicted_positives_500 = 0
        true_positives_400 = 0
        predicted_positives_400 = 0
        true_positives_300 = 0
        predicted_positives_300 = 0
        true_positives_200 = 0
        predicted_positives_200 = 0
        true_positives_100 = 0
        predicted_positives_100 = 0
        true_positives_50 = 0
        predicted_positives_50 = 0
        true_positives_20 = 0
        predicted_positives_20 = 0
        true_positives_10 = 0
        predicted_positives_10 = 0
        true_positives_5 = 0
        predicted_positives_5 = 0

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
                if len(true_source) <= 0:
                    continue

                candidates_500 = [source_filenum[index] for index in top_indices[0:500]]
                candidates_400 = [source_filenum[index] for index in top_indices[0:400]]
                candidates_300 = [source_filenum[index] for index in top_indices[0:300]]
                candidates_200 = [source_filenum[index] for index in top_indices[0:200]]
                candidates_100 = [source_filenum[index] for index in top_indices[0:100]]
                candidates_50 = [source_filenum[index] for index in top_indices[0:50]]
                candidates_20 = [source_filenum[index] for index in top_indices[0:20]]
                candidates_10 = [source_filenum[index] for index in top_indices[0:10]]
                candidates_5 = [source_filenum[index] for index in top_indices[0:5]]
                # for index in top_indices:
                #     if similarity[index] > 0.15:
                #         candidates.append(source_filenum[index])

                true_positives_500 += len(
                    set(candidates_500).intersection(set(true_source))
                )
                predicted_positives_500 += len(candidates_500)

                true_positives_400 += len(
                    set(candidates_400).intersection(set(true_source))
                )
                predicted_positives_400 += len(candidates_400)

                true_positives_300 += len(
                    set(candidates_300).intersection(set(true_source))
                )
                predicted_positives_300 += len(candidates_300)

                true_positives_200 += len(
                    set(candidates_200).intersection(set(true_source))
                )
                predicted_positives_200 += len(candidates_200)

                true_positives_100 += len(
                    set(candidates_100).intersection(set(true_source))
                )
                predicted_positives_100 += len(candidates_100)

                true_positives_50 += len(
                    set(candidates_50).intersection(set(true_source))
                )
                predicted_positives_50 += len(candidates_50)

                true_positives_20 += len(
                    set(candidates_20).intersection(set(true_source))
                )
                predicted_positives_20 += len(candidates_20)

                true_positives_10 += len(
                    set(candidates_10).intersection(set(true_source))
                )
                predicted_positives_10 += len(candidates_10)

                true_positives_5 += len(
                    set(candidates_5).intersection(set(true_source))
                )
                predicted_positives_5 += len(candidates_5)

                actual_positives += len(true_source)

                print("5")
                print(true_positives_5 / actual_positives)
                print(true_positives_5 / predicted_positives_5)
                print("10")
                print(true_positives_10 / actual_positives)
                print(true_positives_10 / predicted_positives_10)
                print("20")
                print(true_positives_20 / actual_positives)
                print(true_positives_20 / predicted_positives_20)
                print("50")
                print(true_positives_50 / actual_positives)
                print(true_positives_50 / predicted_positives_50)
                print("100")
                print(true_positives_100 / actual_positives)
                print(true_positives_100 / predicted_positives_100)
                print("200")
                print(true_positives_200 / actual_positives)
                print(true_positives_200 / predicted_positives_200)
                print("300")
                print(true_positives_300 / actual_positives)
                print(true_positives_300 / predicted_positives_300)
                print("400")
                print(true_positives_400 / actual_positives)
                print(true_positives_400 / predicted_positives_400)
                print("500")
                print(true_positives_500 / actual_positives)
                print(true_positives_500 / predicted_positives_500)

        # recall = true_positives / total_actual_positives
        # precision = true_positives / total_predicted_positives
        # print(recall)
        # print(precision)
        # print("")

        # results[15] = {}
        # results[15]["recall"] = recall
        # results[15]["precision"] = precision

        # with open(os.path.join(curpath, path, "tfidf-results.json"), "w") as f:
        #     json.dump(results, f)
