import os
import json

from documents.models import SuspiciousDocument
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Evaluate yake keywords candidate retrieval method."

    def handle(self, *args, **options):
        curpath = os.path.dirname(__file__)
        doc_nums = SuspiciousDocument.objects.filter(
            language="en", doc_num__lte=10000
        ).values_list("doc_num", flat=True)

        all_keywords = {}
        for doc_num in doc_nums:
            print(doc_num)
            doc = SuspiciousDocument.objects.get(doc_num=doc_num)
            all_keywords[doc_num] = doc.given_plagiarised_source_document()

        with open(
            os.path.join(
                curpath, "../../../../dataset-preprocessed/suspicious-references.json"
            ),
            "w",
        ) as f:
            json.dump(all_keywords, f)
