import os
import json
import fasttext
import numpy as np

from documents.models import Sentence

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Preprocess source sentences"

    def handle(self, *args, **options):
        curpath = os.path.dirname(__file__)
        model = fasttext.load_model(os.path.join(curpath, "../../wiki.en.bin"))

        for i in range(1, 11094):
            sentences = Sentence.objects.filter(document__doc_num=i)
            sent_vectors = []
            for sentence in sentences:
                sent_vector = np.zeros(shape=(300,))
                words = sentence.preprocessed_text.split(",")
                sentence_length = len(words)

                for word in words:
                    sent_vector = np.add(sent_vector, model.get_word_vector(word))

                sent_vectors.append((sent_vector / sentence_length).tolist())

            dir = f"/Volumes/WeiSin/source-sent-vectors/source-document{i}.json"
            with open(dir, "w") as f:
                json.dump(sent_vectors, f)

            self.stdout.write(f"Written {i}")
