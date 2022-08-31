import math
from documents.models import (
    Document,
    SuspiciousDocument,
    GivenPlagiarismCase,
    PlagiarismCase,
)
from django.core.management.base import BaseCommand
from documents.models import post_filter_plag_cases


def intersection(start1, end1, start2, end2):
    intersection = range(
        max(start1, start2),
        min(end1, end2) + 1,
    )
    return list(intersection)


def case_recall_precision(
    sus_intersection, source_intersection, given_case, detected_case
):
    """Recall of the detections in detecting the plagiarism case."""
    sus_doc_num = given_case.sus_document.doc_num
    source_doc_num = given_case.source_document.doc_num
    sus_doc = SuspiciousDocument.objects.get(doc_num=sus_doc_num)
    source_doc = Document.objects.get(doc_num=source_doc_num)

    sus_intersection_len = sum(
        [
            len(sentence.raw_text)
            for sentence in sus_doc.sentences.filter(number__in=sus_intersection)
        ]
    )
    source_intersection_len = sum(
        [
            len(sentence.raw_text)
            for sentence in source_doc.sentences.filter(number__in=source_intersection)
        ]
    )
    intersection_len = sus_intersection_len + source_intersection_len
    return (
        intersection_len / (given_case.sus_length + given_case.source_length),
        intersection_len / (detected_case.sus_length + detected_case.source_length),
    )


def recall_precision(given_cases, detected_cases):
    recall_num_of_cases = given_cases.count()
    precision_num_of_cases = detected_cases.count()
    recall_per_case = []
    precision_per_case = []
    detections_per_case = []

    for given_case in given_cases:
        sus_doc_num = given_case.sus_document.doc_num
        source_doc_num = given_case.source_document.doc_num

        detected_file_case = detected_cases.filter(
            sus_document__doc_num=sus_doc_num, source_document__doc_num=source_doc_num
        )
        num_detections = 0
        for detected_case in detected_file_case:
            sus_intersection = intersection(
                given_case.sus_start_sentence,
                given_case.sus_end_sentence,
                detected_case.sus_start_sentence,
                detected_case.sus_end_sentence,
            )
            source_intersection = intersection(
                given_case.source_start_sentence,
                given_case.source_end_sentence,
                detected_case.source_start_sentence,
                detected_case.source_end_sentence,
            )
            if len(sus_intersection) > 0 and len(source_intersection) > 0:
                num_detections += 1
            if len(sus_intersection) > 0 or len(source_intersection) > 0:
                case_recall, case_precision = case_recall_precision(
                    sus_intersection, source_intersection, given_case, detected_case
                )
                recall_per_case.append(case_recall)
                precision_per_case.append(case_precision)
            detections_per_case.append(num_detections)

    gdetected_cases = sum((num_dets > 0 for num_dets in detections_per_case))
    if gdetected_cases == 0:
        granularity = 1
    else:
        granularity = sum(detections_per_case) / gdetected_cases
    return (
        sum(recall_per_case) / recall_num_of_cases,
        sum(precision_per_case) / precision_num_of_cases,
        granularity,
    )


def plagdet(rec, prec, gran):
    if (rec == 0 and prec == 0) or prec < 0 or rec < 0 or gran < 1:
        return 0
    return ((2 * rec * prec) / (rec + prec)) / math.log(1 + gran, 2)


class Command(BaseCommand):
    help = "Evaluate performance."

    def handle(self, *args, **options):
        sus_doc_start = 9998
        sus_doc_end = 1
        given_plagiarism_cases = GivenPlagiarismCase.objects.filter(
            obfuscation__in=["low", "none"],
            sus_document__doc_num__lte=sus_doc_start,
            sus_document__doc_num__gte=sus_doc_end,
        )
        detected_plagiarism_cases = PlagiarismCase.objects.filter(
            sus_document__doc_num__lte=sus_doc_start,
            sus_document__doc_num__gte=sus_doc_end,
        )

        detected_plagiarism_cases = post_filter_plag_cases(detected_plagiarism_cases)
        print("done post filtering")

        recall_score, precision_score, granularity = recall_precision(
            given_plagiarism_cases, detected_plagiarism_cases
        )
        f1 = 2 * (recall_score * precision_score) / (recall_score + precision_score)
        plagdet_score = plagdet(recall_score, precision_score, granularity)

        print(recall_score)
        print(precision_score)
        print(f1)
        print(granularity)
        print(plagdet_score)
