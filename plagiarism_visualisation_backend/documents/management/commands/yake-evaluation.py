from documents.models import SuspiciousDocument, Document
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Evaluate yake keywords candidate retrieval method."

    def handle(self, *args, **options):
        sus_doc_nums = (
            SuspiciousDocument.objects.filter(language="en")
            .reverse()
            .values_list("doc_num", flat=True)
        )

        for doc_num in sus_doc_nums:
            print(doc_num)
            sus_doc = SuspiciousDocument.objects.get(doc_num=doc_num)
            sources = sus_doc.given_plagiarised_source_document()

            if len(sources) > 0:
                candidates = sus_doc.get_candidates()

                print(len(candidates))
                print(len(sources))
                print(set(candidates).intersection(set(sources)))

            print("")
