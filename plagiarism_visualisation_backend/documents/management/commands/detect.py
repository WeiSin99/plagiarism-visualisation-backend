import json
import random
import numpy as np
from documents.utils import merge_cases, create_plagiarism_case
from sklearn.metrics.pairwise import cosine_similarity

from documents.models import SuspiciousDocument, GivenPlagiarismCase
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Extract keywords using rake"

    def handle(self, *args, **options):
        all_sus_documents = (
            GivenPlagiarismCase.objects.filter(
                obfuscation__in=["low", "none"], sus_document__doc_num__lte=10000
            )
            .order_by("sus_document")
            .values_list("sus_document", flat=True)
            .distinct()
        )
        all_sus_docs = [
            SuspiciousDocument.objects.get(id=id).doc_num for id in all_sus_documents
        ]

        for filenum in all_sus_docs:
            print(filenum)
            # get suspicious document
            suspicious_document = SuspiciousDocument.objects.get(doc_num=filenum)
            if len(suspicious_document.given_plagiarised_source_document()) <= 0:
                continue

            candidates = suspicious_document.get_candidates()

            print(f"length: {len(candidates)}")
            with open(
                f"/volumes/weisin/suspicious-sent-vectors/suspicious-document{filenum}.json",
                "r",
            ) as f:
                suspicious_sent_vectors = json.load(f)

            potential_cases = {}
            for candidate in candidates:
                print(candidate)

                # get source documents
                with open(
                    f"/volumes/weisin/source-sent-vectors/source-document{candidate}.json",
                    "r",
                ) as f:
                    source_sent_vectors = json.load(f)

                # calculate cosine similarities between all suspicious and source sentences
                cosine_similarities = cosine_similarity(
                    suspicious_sent_vectors, source_sent_vectors
                )

                # get sentences pair with the highest similarity score higher than 0.96
                potential_plagiarised_sents = []
                for sus_sentence_num, similarity in enumerate(cosine_similarities):
                    top_similar_sentences = np.argsort(similarity)[::-1]
                    highest_score = similarity[top_similar_sentences[0]]

                    selected_sentences = []
                    for sentence_num in top_similar_sentences:
                        if similarity[sentence_num] == highest_score:
                            selected_sentences.append(sentence_num)
                        else:
                            break

                    for source_sentence_num in selected_sentences:
                        if similarity[source_sentence_num] > 0.97:
                            potential_plagiarised_sents.append(
                                {
                                    "filenum": candidate,
                                    "suspicious_sentence_number": sus_sentence_num,
                                    "source_sentence_number": int(source_sentence_num),
                                    "score": similarity[source_sentence_num],
                                }
                            )

                potential_cases[candidate] = merge_cases(
                    filenum, potential_plagiarised_sents, window=3
                )

            highest_lookup = {}
            for source_file_num, file_case in potential_cases.items():
                filtered_file_case = []
                for case in file_case:
                    if case["thisEnd"] - case["thisStart"] == 0:
                        sent_num = case["thisStart"]

                        if highest_lookup.get(sent_num):
                            detail = highest_lookup[sent_num]

                            if case["averageScore"] > detail[1]:
                                potential_cases[detail[0]] = list(
                                    filter(
                                        lambda x: x["thisStart"] != sent_num,
                                        potential_cases[detail[0]],
                                    )
                                )

                                filtered_file_case.append(case)
                                highest_lookup[sent_num] = (
                                    source_file_num,
                                    case["averageScore"],
                                )
                        else:
                            filtered_file_case.append(case)
                            highest_lookup[sent_num] = (
                                source_file_num,
                                case["averageScore"],
                            )
                    else:
                        filtered_file_case.append(case)

                potential_cases[source_file_num] = filtered_file_case

            for source_file_num, file_case in potential_cases.items():
                if len(file_case) == 0:
                    continue
                else:
                    for case in file_case:
                        create_plagiarism_case(
                            filenum,
                            case["thisStart"],
                            case["thisEnd"],
                            source_file_num,
                            case["sourceStart"],
                            case["sourceEnd"],
                            case["averageScore"],
                        )

        # response = suspicious_document.serialize()
        #
        # with open("result.json", "r") as f:
        #     potential_cases = json.load(f)
        #
        # potential_cases = [
        #     case for file_case in potential_cases["detectedcases"] for case in file_case
        # ]
        #
        # merged_cases = []
        # for case in potential_cases:
        #     within_case = within_range(case, merged_cases)
        #     case_within_case = case_within_range(case, merged_cases)
        #     overlapped_case, overlapped_part = overlapped_range(case, merged_cases)
        #     case_profile = {
        #         "filenum": case["filenum"],
        #         "sourcestart": case["sourcestart"],
        #         "sourceend": case["sourceend"],
        #         "sourcelength": case["sourcelength"],
        #         "sourcenumwords": case["sourcenumwords"],
        #         "averagescore": case["averagescore"],
        #     }
        #
        #     if within_case >= 0:
        #         merged_cases[within_case]["sources"].append(case_profile)
        #     elif case_within_case >= 0:
        #         merged_cases[case_within_case]["thisstart"] = case["thisstart"]
        #         merged_cases[case_within_case]["thisend"] = case["thisend"]
        #         merged_cases[case_within_case]["thislength"] = case["thislength"]
        #         merged_cases[case_within_case]["thisnumwords"] = case["thisnumwords"]
        #         merged_cases[case_within_case]["sources"].append(case_profile)
        #     elif overlapped_case >= 0:
        #         for part in overlapped_part:
        #             merged_cases[overlapped_case]["overlappedsentence"].append(part)
        #
        #         merged_cases.append(
        #             {
        #                 "thisstart": case["thisstart"],
        #                 "thisend": case["thisend"],
        #                 "thislength": case["thislength"],
        #                 "thisnumwords": case["thisnumwords"],
        #                 "overlappedsentence": overlapped_part,
        #                 "sources": [case_profile],
        #             }
        #         )
        #     else:
        #         merged_cases.append(
        #             {
        #                 "thisstart": case["thisstart"],
        #                 "thisend": case["thisend"],
        #                 "thislength": case["thislength"],
        #                 "thisnumwords": case["thisnumwords"],
        #                 "overlappedsentence": [],
        #                 "sources": [case_profile],
        #             }
        #         )
        #
        # merged_cases = sorted(merged_cases, key=lambda x: x["thisstart"])
        #
        # processed_merged_cases = []
        # for merged_case in merged_cases:
        #     if merged_case["thisnumwords"] <= 2:
        #         continue
        #
        #     processed_merged_case = merged_case
        #     sources = list(
        #         filter(
        #             lambda c: abs(merged_case["thisnumwords"] - c["sourcenumwords"])
        #             <= 25
        #             and c["sourcenumwords"] > 2,
        #             merged_case["sources"],
        #         )
        #     )
        #     processed_merged_case["sources"] = sorted(
        #         sources, key=lambda s: s["averagescore"]
        #     )
        #     if len(processed_merged_case["sources"]) > 0:
        #         processed_merged_cases.append(processed_merged_case)
        #
        # response = suspicious_document.serialize()
        # response["detectedcases"] = processed_merged_cases
