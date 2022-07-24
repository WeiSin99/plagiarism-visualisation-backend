import os
import re
from slugify import slugify
import xml.etree.ElementTree as ET
from nltk.tokenize import sent_tokenize

from documents.models import SuspiciousDocument, SuspiciousSentence

from django.core.management.base import BaseCommand


def get_document_metadata(path):
    title = authors = language = None
    xml_tree = ET.parse(path)
    for child in xml_tree.getroot():
        if child.tag == "feature" and child.get("name") == "about":
            title = child.get("title")
            authors = child.get("authors")
            language = child.get("lang")

    return (title, authors, language)


def generate_document_slug(title):
    slug = slugify(title)
    num_existing_slug = SuspiciousDocument.objects.filter(slug__startswith=slug).count()
    if num_existing_slug == 0:
        return slug
    return f"{slug}{num_existing_slug+1}"


class Command(BaseCommand):
    help = "Populate database with document dataset"

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            default="../../../../dataset-raw/suspicious-document",
            help="Path to documents",
        )

    def handle(self, *args, **options):
        curpath = os.path.dirname(__file__)
        source_path = os.path.join(curpath, options["path"])

        # loop through the directory
        for dirpath, _, files in os.walk(source_path):
            if dirpath == source_path:
                continue

            if os.path.basename(dirpath) != "part23":
                continue

            for file in files:
                if file == ".DS_Store" or file.endswith(".xml"):
                    continue

                filename, _ = os.path.splitext(os.path.basename(file))
                file_number = re.search(r"\d+", filename)
                file_number = file_number and int(file_number.group())

                with open(os.path.join(dirpath, f"{filename}.txt")) as f:
                    text = f.read()

                title, _, language = get_document_metadata(
                    os.path.join(dirpath, f"{filename}.xml")
                )
                title = title or filename

                # writing into database
                document_model = SuspiciousDocument.objects.create(
                    title=title,
                    slug=generate_document_slug(title),
                    doc_num=file_number,
                    language=language,
                    raw_text=text,
                )

                # if authors:
                #     for author in authors.split(","):
                #         author_model, _ = Author.objects.get_or_create(
                #             name=author, slug=slugify(author)
                #         )
                #         author_model.document.add(document_model)

                sentences = sent_tokenize(text)
                for i, sentence in enumerate(sentences):
                    SuspiciousSentence.objects.create(
                        raw_text=sentence, document=document_model, number=i
                    )

                self.stdout.write(f"Written {filename}")
