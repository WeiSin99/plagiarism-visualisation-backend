import json

from documents.models import (
    Document,
    SuspiciousDocument,
    GivenPlagiarismCase,
    PlagiarismCase,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Extract keywords using rake"

    def handle(self, *args, **options):
        sus_doc_num = 9975
        sus_start = 2066
        sus_end = 2067

        source_doc_num = 9975
        source_start = 771
        source_end = 771

        source_document = Document.objects.get(doc_num=source_doc_num)
        suspicious_document = SuspiciousDocument.objects.get(doc_num=sus_doc_num)
        given_sources = suspicious_document.given_plagiarised_source_document()

        for case in GivenPlagiarismCase.objects.filter(
            sus_document__doc_num=sus_doc_num
        ).order_by("sus_start_sentence"):
            print(case)
        print("")

        # detected_cases = (
        #     PlagiarismCase.objects.filter(sus_document__doc_num=sus_doc_num)
        #     .filter(source_document__doc_num__in=given_sources)
        #     .order_by("sus_start_sentence")
        # )
        detected_cases = (
            PlagiarismCase.objects.filter(sus_document__doc_num=sus_doc_num)
            .exclude(source_document__doc_num__in=given_sources)
            .order_by("sus_start_sentence")
        )
        # detected_cases = PlagiarismCase.objects.filter(
        #     sus_document__doc_num=sus_doc_num
        # ).order_by("sus_start_sentence")

        filtered_plagiarism_cases = []
        for case in detected_cases:
            word_difference_threshold = 0.7
            single_sentence_score_threshold = 0.975

            if (
                min(case.sus_word_len, case.source_word_len)
                / max(case.sus_word_len, case.source_word_len)
                > word_difference_threshold
            ):
                if (
                    case.sus_end_sentence - case.sus_start_sentence == 0
                    or case.source_end_sentence - case.source_start_sentence == 0
                ):
                    if case.score > single_sentence_score_threshold:
                        filtered_plagiarism_cases.append(case.id)
                else:
                    filtered_plagiarism_cases.append(case.id)

        detected_cases = PlagiarismCase.objects.filter(id__in=filtered_plagiarism_cases)

        print(detected_cases.count())
        for case in detected_cases:
            print(case)

        # print("")
        # suspicious_sentences = suspicious_document.sentences.filter(
        #     number__gte=sus_start, number__lte=sus_end
        # )
        # source_sentences = source_document.sentences.filter(
        #     number__gte=source_start, number__lte=source_end
        # )
        #
        # print(" ".join([sentence.raw_text for sentence in suspicious_sentences]))
        # print()
        # print(" ".join([sentence.raw_text for sentence in source_sentences]))
        # print(
        #     PlagiarismCase.objects.get(
        #         sus_document=suspicious_document,
        #         source_document=source_document,
        #         sus_start_sentence=sus_start,
        #         sus_end_sentence=sus_end,
        #         source_start_sentence=source_start,
        #         source_end_sentence=source_end,
        #     ).score
        # )
