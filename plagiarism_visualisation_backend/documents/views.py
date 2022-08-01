import json
import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity

from django.http import JsonResponse

from .models import Document, SuspiciousDocument
from .utils import (
    assign_sentence_number,
    merge_cases,
    within_range,
    case_within_range,
    overlapped_range,
)


def suspicious_document_detail(request, filenum):
    response = {}
    if request.method == "GET":
        suspicious_document = SuspiciousDocument.objects.get(doc_num=filenum)
        db_sentences = [
            sentence.serialize() for sentence in suspicious_document.sentences.all()
        ]

        document_raw_text = suspicious_document.raw_text
        if document_raw_text.startswith("\ufeff"):
            document_raw_text = document_raw_text[1:]
        paragraphs = document_raw_text.split("\n\n")
        splitted_paragraphs = [sent_tokenize(paragraph) for paragraph in paragraphs]

        processed_paragraphs = assign_sentence_number(
            splitted_paragraphs, db_sentences, "suspicious", filenum
        )

        response = suspicious_document.serialize()
        response["sentenceLength"] = db_sentences[-1]["number"]
        response["processedLength"] = processed_paragraphs[-2][-1]["number"]
        response["processedParagraphs"] = processed_paragraphs

    return JsonResponse(response)


def source_document_detail(request, filenum):
    response = {}
    if request.method == "GET":
        suspicious_document = Document.objects.get(doc_num=filenum)
        db_sentences = [
            sentence.serialize() for sentence in suspicious_document.sentences.all()
        ]

        document_raw_text = suspicious_document.raw_text
        if document_raw_text.startswith("\ufeff"):
            document_raw_text = document_raw_text[1:]
        paragraphs = document_raw_text.split("\n\n")
        splitted_paragraphs = [sent_tokenize(paragraph) for paragraph in paragraphs]

        processed_paragraphs = assign_sentence_number(
            splitted_paragraphs, db_sentences, "source", filenum
        )

        response = suspicious_document.serialize()
        response["sentenceLength"] = db_sentences[-1]["number"]
        response["processedLength"] = processed_paragraphs[-2][-1]["number"]
        response["processedParagraphs"] = processed_paragraphs

    return JsonResponse(response)


# Create your views here.
def detail_analysis(request, filenum):
    """Detail analysis of a suspicious document"""
    response = {}

    if request.method == "GET":
        # # get suspicious document
        suspicious_document = SuspiciousDocument.objects.get(doc_num=filenum)
        # suspicious_sentences = suspicious_document.sentences.all()
        # suspicious_sent_vectors = [
        #     json.loads(sentence.fasttext_vector) for sentence in suspicious_sentences
        # ]
        #
        # for i in range(5000, 6000):
        #     # get source documents
        #     source_document = Document.objects.get(doc_num=i)
        #     source_sentences = source_document.sentences.all()
        #     # source_sentences = filter(
        #     #     lambda s: len(s.preprocessed_text.split(",")) > 2, source_sentences
        #     # )
        #     source_sent_vectors = [
        #         json.loads(sentence.fasttext_vector) for sentence in source_sentences
        #     ]
        #
        #     # calculate cosine similarities between all suspicious and source sentences
        #     cosine_similarities = cosine_similarity(
        #         suspicious_sent_vectors, source_sent_vectors
        #     )
        #
        #     # get sentences pair with the highest similarity score higher than 0.96
        #     potential_plagiarised_sents = []
        #     top_n = 5
        #     for sus_sentence_num, similarity in enumerate(cosine_similarities):
        #         top_similar_sentence = np.argsort(similarity)[::-1][:top_n]
        #         for source_sentence_num in top_similar_sentence:
        #             if similarity[source_sentence_num] > 0.975:
        #                 potential_plagiarised_sents.append(
        #                     {
        #                         "filenum": i,
        #                         "suspicious_sentence_number": sus_sentence_num,
        #                         "source_sentence_number": int(source_sentence_num),
        #                         "score": similarity[source_sentence_num],
        #                     }
        #                 )
        #
        #     potential_cases.append(
        #         merge_cases(filenum, potential_plagiarised_sents, window=3)
        #     )
        #
        # potential_cases = list(filter(lambda c: len(c) > 0, potential_cases))
        # with open("result.json", "w") as f:
        #     json.dump({"detectedCases": potential_cases}, f)

        # response = suspicious_document.serialize()

        with open("result.json", "r") as f:
            potential_cases = json.load(f)

        potential_cases = [
            case for file_case in potential_cases["detectedCases"] for case in file_case
        ]

        merged_cases = []
        for case in potential_cases:
            within_case = within_range(case, merged_cases)
            case_within_case = case_within_range(case, merged_cases)
            overlapped_case, overlapped_part = overlapped_range(case, merged_cases)
            if within_case >= 0:
                merged_cases[within_case]["sources"].append(
                    {
                        "filenum": case["filenum"],
                        "sourceStart": case["sourceStart"],
                        "sourceEnd": case["sourceEnd"],
                        "sourceLength": case["sourceLength"],
                        "sourceNumWords": case["sourceNumWords"],
                        "averageScore": case["averageScore"],
                    }
                )
            elif case_within_case >= 0:
                merged_cases[case_within_case]["thisStart"] = case["thisStart"]
                merged_cases[case_within_case]["thisEnd"] = case["thisEnd"]
                merged_cases[case_within_case]["thisLength"] = case["thisLength"]
                merged_cases[case_within_case]["thisNumWords"] = case["thisNumWords"]
                merged_cases[case_within_case]["sources"].append(
                    {
                        "filenum": case["filenum"],
                        "sourceStart": case["sourceStart"],
                        "sourceEnd": case["sourceEnd"],
                        "sourceLength": case["sourceLength"],
                        "sourceNumWords": case["sourceNumWords"],
                        "averageScore": case["averageScore"],
                    }
                )
            elif overlapped_case >= 0:
                for part in overlapped_part:
                    merged_cases[overlapped_case]["overlappedSentence"].append(part)

                merged_cases.append(
                    {
                        "thisStart": case["thisStart"],
                        "thisEnd": case["thisEnd"],
                        "thisLength": case["thisLength"],
                        "thisNumWords": case["thisNumWords"],
                        "overlappedSentence": overlapped_part,
                        "sources": [
                            {
                                "filenum": case["filenum"],
                                "sourceStart": case["sourceStart"],
                                "sourceEnd": case["sourceEnd"],
                                "sourceLength": case["sourceLength"],
                                "sourceNumWords": case["sourceNumWords"],
                                "averageScore": case["averageScore"],
                            }
                        ],
                    }
                )
            else:
                merged_cases.append(
                    {
                        "thisStart": case["thisStart"],
                        "thisEnd": case["thisEnd"],
                        "thisLength": case["thisLength"],
                        "thisNumWords": case["thisNumWords"],
                        "overlappedSentence": [],
                        "sources": [
                            {
                                "filenum": case["filenum"],
                                "sourceStart": case["sourceStart"],
                                "sourceEnd": case["sourceEnd"],
                                "sourceLength": case["sourceLength"],
                                "sourceNumWords": case["sourceNumWords"],
                                "averageScore": case["averageScore"],
                            }
                        ],
                    }
                )

        merged_cases = sorted(merged_cases, key=lambda x: x["thisStart"])

        processed_merged_cases = []
        for merged_case in merged_cases:
            if merged_case["thisNumWords"] <= 2:
                continue

            processed_merged_case = merged_case
            sources = list(
                filter(
                    lambda c: abs(merged_case["thisNumWords"] - c["sourceNumWords"])
                    <= 25
                    and c["sourceNumWords"] > 2,
                    merged_case["sources"],
                )
            )
            processed_merged_case["sources"] = sorted(
                sources, key=lambda s: s["averageScore"]
            )
            if len(processed_merged_case["sources"]) > 0:
                processed_merged_cases.append(processed_merged_case)

        response = suspicious_document.serialize()
        response["detectedCases"] = processed_merged_cases

    return JsonResponse(response)
