import os
import json
import fasttext
import numpy as np

from documents.models import SuspiciousSentence

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Preprocess source sentences"

    def handle(self, *args, **options):
        curpath = os.path.dirname(__file__)
        model = fasttext.load_model(os.path.join(curpath, "../../wiki.en.bin"))

        for i in range(2964, 2965):
            sentences = SuspiciousSentence.objects.filter(document__doc_num=i)
            for sentence in sentences:
                sent_vector = np.zeros(shape=(300,))
                words = sentence.preprocessed_text.split(",")
                sentence_length = len(words)

                for word in words:
                    sent_vector = np.add(sent_vector, model.get_word_vector(word))

                sentence.fasttext_vector = json.dumps(
                    (sent_vector / sentence_length).tolist()
                )

                sentence.save()

            self.stdout.write(f"Written {i}")
