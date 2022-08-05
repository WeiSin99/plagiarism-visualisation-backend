import pke
import json
import math

from documents.models import SuspiciousDocument, Document
from django.core.management.base import BaseCommand


def further_filter_candidates(extractor):
    for k in list(extractor.candidates):

        # get the candidate
        v = extractor.candidates[k]

        # filter candidates starting/ending with a stopword or containing
        # a first/last word with less than 3 characters
        if (
            v.surface_forms[0][0].lower() in extractor.stoplist
            or v.surface_forms[0][-1].lower() in extractor.stoplist
            or len(v.surface_forms[0][0]) < 3
            or len(v.surface_forms[0][-1]) < 3
        ):
            del extractor.candidates[k]


class Command(BaseCommand):
    help = "Extract suspicious keywords"

    def handle(self, *args, **options):
        extractor = pke.unsupervised.YAKE()

        suspicious_document = SuspiciousDocument.objects.get(doc_num=10497)
        extractor.load_document(
            input=suspicious_document.raw_text,
            language="en",
        )
        extractor.ngram_selection(n=3)
        extractor.candidate_filtering(pos_blacklist=["VERB", "NUM"])
        further_filter_candidates(extractor)
        extractor.candidate_weighting()

        suspicious_keywords = []
        for keyword, _ in extractor.get_n_best(n=50, stemming=False):
            suspicious_keywords.append(keyword)

        candidates = []
        source_documents = Document.objects.filter(
            language="en", doc_num__gte=10000
        ).values_list("doc_num", flat=True)
        for doc_num in source_documents:
            source_keywords = json.loads(Document.objects.get(doc_num=doc_num).keywords)
            common_keywords = set(suspicious_keywords).intersection(
                set(source_keywords)
            )
            if len(common_keywords) > 2:
                candidates.append(doc_num)

        print(len(candidates))
        print(10933 in candidates)
        print(10492 in candidates)
        print(10804 in candidates)
