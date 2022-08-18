from nltk.tokenize import sent_tokenize

from documents.models import Document, SuspiciousDocument
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Extract keywords using rake"

    def handle(self, *args, **options):
        documents = SuspiciousDocument.objects.all().values_list("doc_num", flat=True)
        for doc_num in documents:
            print(doc_num)
            document = SuspiciousDocument.objects.get(doc_num=doc_num)
            all_sentences = document.sentences.all()

            paragraphs = document.raw_text.split("\n\n")
            splitted_paragraphs = [sent_tokenize(paragraph) for paragraph in paragraphs]
            start_sentence = -1
            for paragraph in splitted_paragraphs:
                if len(paragraph) > 0:
                    sentences = all_sentences.filter(number__gt=start_sentence)
                    for sentence in sentences:
                        if sentence.raw_text == paragraph[-1]:
                            sentence.raw_text = sentence.raw_text + "\n\n"
                            start_sentence = sentence.number
                            sentence.save()
                            break
