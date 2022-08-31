import os
import math
import json
import pickle
import numpy as np
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

from documents.models import Document, SuspiciousDocument
from django.core.management.base import BaseCommand


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV,
    }

    return tag_dict.get(tag, wordnet.NOUN)


class Command(BaseCommand):
    help = "Preprocess source sentences"

    def handle(self, *args, **options):
        curpath = os.path.dirname(__file__)
        dataset_path = "../../../../dataset-preprocessed"
        with open(
            os.path.join(curpath, dataset_path, "bm25_plus.pickle"), "rb"
        ) as model_file:
            bm25 = pickle.load(model_file)

        english_doc_nums = Document.objects.filter(language="en").values_list(
            "doc_num", flat=True
        )
        sus_doc_nums = SuspiciousDocument.objects.all().values_list(
            "doc_num", flat=True
        )

        all_actual_positives = 0

        all_true_positives_500 = 0
        all_predicted_positives_500 = 0
        all_true_positives_400 = 0
        all_predicted_positives_400 = 0
        all_true_positives_300 = 0
        all_predicted_positives_300 = 0
        all_true_positives_200 = 0
        all_predicted_positives_200 = 0
        all_true_positives_100 = 0
        all_predicted_positives_100 = 0
        all_true_positives_50 = 0
        all_predicted_positives_50 = 0
        all_true_positives_20 = 0
        all_predicted_positives_20 = 0
        all_true_positives_10 = 0
        all_predicted_positives_10 = 0
        all_true_positives_5 = 0
        all_predicted_positives_5 = 0

        # total_candidates = 0
        # num_of_doc = 0
        for doc_num in sus_doc_nums:
            print(doc_num)
            part_number = math.ceil(doc_num / 500)
            doc = SuspiciousDocument.objects.get(doc_num=doc_num)
            given_sources = doc.given_plagiarised_source_document()
            if len(given_sources) <= 0:
                continue

            with open(
                os.path.join(
                    curpath,
                    dataset_path,
                    "keywords/",
                    f"part{part_number}-keywords.json",
                ),
                "r",
            ) as kw_file:
                keywords = json.load(kw_file)[str(doc_num)]

            all_candidates = {}
            lemmatizer = WordNetLemmatizer()
            for keyword in keywords:
                processed_keywords = [
                    lemmatizer.lemmatize(word, get_wordnet_pos(word))
                    for word in keyword
                ]

                doc_scores = bm25.get_scores(processed_keywords)
                top_indices = np.argsort(doc_scores)[::-1]

                for index in top_indices[0:10]:
                    english_doc_num = english_doc_nums[int(index)]
                    if all_candidates.get(english_doc_num):
                        if doc_scores[int(index)] > all_candidates[english_doc_num]:
                            all_candidates[english_doc_num] = doc_scores[int(index)]
                    else:
                        all_candidates[english_doc_num] = doc_scores[int(index)]

            # total_candidates += len(all_candidates)
            # num_of_doc += 1
            # print(total_candidates)
            # print(num_of_doc)
            # print()

            all_candidates_500 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:500]
            all_candidates_500 = list(set(all_candidates_500))
            all_true_positives_500 += len(
                set(all_candidates_500).intersection(set(given_sources))
            )
            all_predicted_positives_500 += len(all_candidates_500)

            all_candidates_400 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:400]
            all_candidates_400 = list(set(all_candidates_400))
            all_true_positives_400 += len(
                set(all_candidates_400).intersection(set(given_sources))
            )
            all_predicted_positives_400 += len(all_candidates_400)

            all_candidates_300 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:300]
            all_candidates_300 = list(set(all_candidates_300))
            all_true_positives_300 += len(
                set(all_candidates_300).intersection(set(given_sources))
            )
            all_predicted_positives_300 += len(all_candidates_300)

            all_candidates_200 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:200]
            all_candidates_200 = list(set(all_candidates_200))
            all_true_positives_200 += len(
                set(all_candidates_200).intersection(set(given_sources))
            )
            all_predicted_positives_200 += len(all_candidates_200)

            all_candidates_100 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:100]
            all_candidates_100 = list(set(all_candidates_100))
            all_true_positives_100 += len(
                set(all_candidates_100).intersection(set(given_sources))
            )
            all_predicted_positives_100 += len(all_candidates_100)

            all_candidates_50 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:50]
            all_candidates_50 = list(set(all_candidates_50))
            all_true_positives_50 += len(
                set(all_candidates_50).intersection(set(given_sources))
            )
            all_predicted_positives_50 += len(all_candidates_50)

            all_candidates_20 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:20]
            all_candidates_20 = list(set(all_candidates_20))
            all_true_positives_20 += len(
                set(all_candidates_20).intersection(set(given_sources))
            )
            all_predicted_positives_20 += len(all_candidates_20)

            all_candidates_10 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:10]
            all_candidates_10 = list(set(all_candidates_10))
            all_true_positives_10 += len(
                set(all_candidates_10).intersection(set(given_sources))
            )
            all_predicted_positives_10 += len(all_candidates_10)

            all_candidates_5 = [
                k
                for k, _ in sorted(
                    all_candidates.items(), key=lambda item: item[1], reverse=True
                )
            ][0:5]
            all_candidates_5 = list(set(all_candidates_5))
            all_true_positives_5 += len(
                set(all_candidates_5).intersection(set(given_sources))
            )
            all_predicted_positives_5 += len(all_candidates_5)

            all_actual_positives += len(given_sources)

            print("5")
            print(all_true_positives_5 / all_actual_positives)
            print(all_true_positives_5 / all_predicted_positives_5)
            print("10")
            print(all_true_positives_10 / all_actual_positives)
            print(all_true_positives_10 / all_predicted_positives_10)
            print("20")
            print(all_true_positives_20 / all_actual_positives)
            print(all_true_positives_20 / all_predicted_positives_20)
            print("50")
            print(all_true_positives_50 / all_actual_positives)
            print(all_true_positives_50 / all_predicted_positives_50)
            print("100")
            print(all_true_positives_100 / all_actual_positives)
            print(all_true_positives_100 / all_predicted_positives_100)
            print("200")
            print(all_true_positives_200 / all_actual_positives)
            print(all_true_positives_200 / all_predicted_positives_200)
            print("300")
            print(all_true_positives_300 / all_actual_positives)
            print(all_true_positives_300 / all_predicted_positives_300)
            print("400")
            print(all_true_positives_400 / all_actual_positives)
            print(all_true_positives_400 / all_predicted_positives_400)
            print("500")
            print(all_true_positives_500 / all_actual_positives)
            print(all_true_positives_500 / all_predicted_positives_500)
            print("")
