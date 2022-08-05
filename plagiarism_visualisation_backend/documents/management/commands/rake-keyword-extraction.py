import json
import string
from rake_nltk import Rake

from documents.models import SuspiciousDocument, Document
from django.core.management.base import BaseCommand


def postprocess_keywords(keywords):
    processed_score_keywords = []
    for score, keyword in keywords:
        processed_keyword = " ".join(
            keyword.translate(str.maketrans("", "", string.punctuation)).split()
        )
        processed_score_keywords.append((score, processed_keyword))

    return processed_score_keywords


def get_keywords(keywords):
    filtered_keywords = []
    for score, keyword in keywords:
        if score > 2:
            filtered_keywords.append(keyword)

    return filtered_keywords


class Command(BaseCommand):
    help = "Extract keywords using rake"

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            type=str,
            choices=["source", "suspicious"],
            help="Type of documents to be preprocessed.",
        )

    def handle(self, *args, **options):
        rake = Rake(
            language="english",
            include_repeated_phrases=False,
            min_length=1,
            max_length=4,
        )

        documents = []
        if options["type"] == "source":
            documents = Document.objects.filter(language="en").values_list(
                "doc_num", flat=True
            )
        elif options["type"] == "suspicious":
            documents = SuspiciousDocument.objects.filter(language="en").values_list(
                "doc_num", flat=True
            )

        for doc_num in documents:
            if options["type"] == "source":
                document = Document.objects.get(doc_num=doc_num)
            else:
                document = SuspiciousDocument.objects.get(doc_num=doc_num)

            rake.extract_keywords_from_text(document.raw_text)
            keywords = postprocess_keywords(rake.get_ranked_phrases_with_scores())
            document.keywords = json.dumps(keywords)
            document.save()
            print(doc_num)

        # evaluation
        # suspicious_document = SuspiciousDocument.objects.get(doc_num=10964)
        # suspicious_keywords = set(
        #     get_keywords(json.loads(suspicious_document.keywords))
        # )
        # threshold = int(len(suspicious_keywords) * 0.02)
        #
        # candidates = []
        # source_documents = Document.objects.filter(language="en").values_list(
        #     "doc_num", flat=True
        # )
        # for doc_num in source_documents:
        #     source_document = Document.objects.get(doc_num=doc_num)
        #     source_keywords = set(get_keywords(json.loads(source_document.keywords)))
        #
        #     if len(suspicious_keywords.intersection(source_keywords)) > threshold:
        #         candidates.append(doc_num)
        #
        # print(candidates)
        # print(len(candidates))
