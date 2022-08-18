import os
import json

from django.http import JsonResponse

from .models import Document, SuspiciousDocument
from .utils import intersection


def suspicious_document_detail(request, filenum):
    response = {}
    if request.method == "GET":
        suspicious_document = SuspiciousDocument.objects.get(doc_num=filenum)
        db_sentences = [
            sentence.serialize() for sentence in suspicious_document.sentences.all()
        ]

        response = suspicious_document.serialize()
        response["sentences"] = db_sentences

    return JsonResponse(response)


def source_document_detail(request, filenum):
    response = {}
    if request.method == "GET":
        suspicious_document = Document.objects.get(doc_num=filenum)
        db_sentences = [
            sentence.serialize() for sentence in suspicious_document.sentences.all()
        ]

        response = suspicious_document.serialize()
        response["sentences"] = db_sentences

    return JsonResponse(response)


def corpus_view(request, corpus_num):
    response = []
    if request.method == "GET":
        curpath = os.path.dirname(__file__)
        path = "../../dataset-preprocessed"
        with open(os.path.join(curpath, path, f"corpus{corpus_num}.json"), "r") as f:
            corpus = json.load(f)

        response = []
        for source_doc_num in corpus["source_documents"]:
            document = Document.objects.get(doc_num=source_doc_num)
            sources = list(
                filter(
                    lambda s: s in corpus["suspicious_documents"],
                    document.given_plagiarised_suspicious_document(),
                )
            )
            response_dict = document.serialize()
            response_dict["id"] = f"source-{source_doc_num}"
            response_dict["score"] = document.plagiarism_score()
            response_dict["sources"] = [f"suspicious-{source}" for source in sources]
            response.append(response_dict)

        for suspicious_doc_num in corpus["suspicious_documents"]:
            document = SuspiciousDocument.objects.get(doc_num=suspicious_doc_num)
            sources = filter(
                lambda s: s in corpus["source_documents"],
                document.given_plagiarised_source_document(),
            )
            response_dict = document.serialize()
            response_dict["id"] = f"suspicious-{suspicious_doc_num}"
            response_dict["score"] = document.plagiarism_score()
            response_dict["sources"] = [f"source-{source}" for source in sources]
            response.append(response_dict)

        response = sorted(response, key=lambda x: x["score"], reverse=True)
        return JsonResponse({"response": response})


def detail_analysis(request, type, filenum):
    """Detail analysis of a suspicious document"""
    response = {}
    if request.method == "GET":
        if type == "source":
            doc = Document.objects.get(doc_num=filenum)
        elif type == "suspicious":
            doc = SuspiciousDocument.objects.get(doc_num=filenum)
        else:
            return JsonResponse(response)

        doc_len = len(doc.raw_text)
        response = doc.serialize()
        response["plagiarismScore"] = doc.plagiarism_score()
        response["charLength"] = doc_len

        # post filtering
        detected_plagiarism_cases = doc.detected_plagiarism_cases()

        # detected cases response
        detected_cases = []
        for case in detected_plagiarism_cases:
            case_response = case.serialize(type)
            case_response["plagiarisedPercent"] = case_response["thisLength"] / doc_len
            detected_cases.append(case_response)

        intersected_cases = []
        for case in range(len(detected_cases) - 1):
            for compare_case in range(case + 1, len(detected_cases)):
                source_case = detected_cases[case]
                target_case = detected_cases[compare_case]

                intersected_sentences = intersection(
                    source_case["thisStart"],
                    source_case["thisEnd"],
                    target_case["thisStart"],
                    target_case["thisEnd"],
                )

                if len(intersected_sentences) > 0:
                    intersected_cases.append(
                        {
                            "source": case,
                            "target": compare_case,
                            "intersected_sentences": intersected_sentences,
                        }
                    )

        # plagiarism sources
        detected_sources = {}
        for case in detected_cases:
            if detected_sources.get(case["filenum"]):
                detected_sources[case["filenum"]] += case["plagiarisedPercent"]
            else:
                detected_sources[case["filenum"]] = case["plagiarisedPercent"]

        detected_sources_detail = []
        for filenum, percentage in detected_sources.items():
            doc_title = ""
            if type == "source":
                doc_title = SuspiciousDocument.objects.get(doc_num=filenum).title
            elif type == "suspicious":
                doc_title = Document.objects.get(doc_num=filenum).title

            detected_sources_detail.append(
                {
                    "filenum": filenum,
                    "title": doc_title,
                    "percentage": percentage,
                }
            )

        # cannot sort detected_cases here can only sort when querying
        detected_sources_detail = sorted(
            detected_sources_detail, key=lambda x: x["percentage"], reverse=True
        )
        response["detectedSources"] = detected_sources_detail
        response["intersectedCases"] = intersected_cases
        response["detectedCases"] = detected_cases
    return JsonResponse(response)
