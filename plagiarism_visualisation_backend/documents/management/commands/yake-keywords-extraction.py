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

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            type=str,
            choices=["source", "suspicious"],
            help="Type of documents to be preprocessed.",
        )

    def handle(self, *args, **options):
        if options["type"] == "source":
            documents = Document.objects.filter(language="en").values_list(
                "doc_num", flat=True
            )
        else:
            documents = SuspiciousDocument.objects.filter(language="en").values_list(
                "doc_num", flat=True
            )

        extractor = pke.unsupervised.YAKE()
        for doc_num in documents:
            if options["type"] == "source":
                document = Document.objects.get(doc_num=doc_num)
            else:
                document = SuspiciousDocument.objects.get(doc_num=doc_num)

            text_length = len(document.raw_text)
            keywords = []
            for i in range(0, math.ceil(text_length / 1000000)):
                extractor.load_document(
                    input=document.raw_text[1000000 * i : 1000000 * (i + 1)],
                    language="en",
                )
                extractor.ngram_selection(n=3)
                extractor.candidate_filtering(pos_blacklist=["VERB", "NUM"])
                further_filter_candidates(extractor)
                extractor.candidate_weighting()

                for keyword, _ in extractor.get_n_best(n=50, stemming=False):
                    keywords.append(keyword)

            print(doc_num)
            print("")
            document.keywords = json.dumps(list(set(keywords)))
            document.save()
