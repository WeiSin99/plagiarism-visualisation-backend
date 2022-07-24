import string
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag

from documents.models import Sentence

from django.core.management.base import BaseCommand


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV,
    }

    return tag_dict.get(tag, wordnet.NOUN)


class Command(BaseCommand):
    help = "Preprocess source sentences"

    def handle(self, *args, **options):
        # sentences = Sentence.objects.filter(number=0)
        # for sentence in sentences:
        #     if sentence.raw_text.startswith("\ufeff"):
        #         sentence.raw_text = sentence.raw_text[1:]
        #         sentence.save()

        for i in range(9472, 11094):
            sentences = Sentence.objects.filter(document__doc_num=i)
            for sentence in sentences:
                raw_text = sentence.raw_text
                if raw_text.startswith("\ufeff"):
                    raw_text = raw_text[1:]
                    sentence.raw_text = raw_text
                word_token = word_tokenize(raw_text.lower())
                lemmatizer = WordNetLemmatizer()

                processed_token = []
                for word in word_token:
                    if (not word in string.punctuation) and (word.isalnum()):
                        lemmatized_word = lemmatizer.lemmatize(
                            word, get_wordnet_pos(word)
                        )
                        processed_token.append(lemmatized_word)

                sentence.preprocessed_text = ",".join(processed_token)
                sentence.save()

            self.stdout.write(f"Written {i}")
