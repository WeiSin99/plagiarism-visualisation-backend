import os
import math
import xml.etree.ElementTree as ET

from documents.models import GivenPlagiarismCase
from documents.models import SuspiciousDocument, Document

from django.core.management.base import BaseCommand


def get_sentences(file_number, type, start_sentence, end_sentence):
    if type == "source":
        sentences = Document.objects.get(doc_num=file_number).sentences.filter(
            number__gte=start_sentence, number__lte=end_sentence
        )
    else:
        sentences = SuspiciousDocument.objects.get(
            doc_num=file_number
        ).sentences.filter(number__gte=start_sentence, number__lte=end_sentence)

    text = ""
    for sentence in sentences:
        text += f"{sentence.raw_text} "

    return text


def get_document_part(file_number, type, part):
    if type == "source":
        text = Document.objects.get(doc_num=file_number).raw_text
    else:
        text = SuspiciousDocument.objects.get(doc_num=file_number).raw_text

    text = text[int(part[0]) : (int(part[0]) + int(part[1]))]

    return text


def get_plagiarised_part(file_number):
    curpath = os.path.dirname(__file__)
    xml_source_path = "../../../../dataset-raw/suspicious-document"
    part_number = math.ceil(file_number / 500)
    xml_file = (
        f"part{part_number}/suspicious-document{str(file_number).rjust(5, '0')}.xml"
    )

    cases = []
    xml_tree = ET.parse(os.path.join(curpath, xml_source_path, xml_file))
    for child in xml_tree.getroot():
        if (
            child.tag == "feature"
            and child.get("name") == "plagiarism"
            and child.get("type") != "translation"
        ):
            plagiarism_source = int(
                child.get("source_reference", "0").split(".")[0][-5:]
            )
            source_part = (child.get("source_offset"), child.get("source_length"))
            plagiarised_part = (child.get("this_offset"), child.get("this_length"))
            obfuscation = child.get("obfuscation")
            type = child.get("type")
            cases.append(
                [
                    plagiarism_source,
                    obfuscation,
                    get_document_part(file_number, "suspicious", plagiarised_part),
                    get_document_part(plagiarism_source, "source", source_part),
                    type,
                ]
            )

    return cases


def create_given_case(
    sus_doc_num,
    sus_start,
    sus_end,
    source_doc_num,
    source_start,
    source_end,
    obfuscation,
    type,
):
    sus_doc = SuspiciousDocument.objects.get(doc_num=sus_doc_num)
    sus_sentences = sus_doc.sentences.filter(number__gte=sus_start, number__lte=sus_end)
    sus_len = sum([len(sus_sentence.raw_text) for sus_sentence in sus_sentences])
    sus_word_len = sum(
        [
            len(sus_sentence.preprocessed_text.split(","))
            for sus_sentence in sus_sentences
        ]
    )

    source_doc = Document.objects.get(doc_num=source_doc_num)
    source_sentences = source_doc.sentences.filter(
        number__gte=source_start, number__lte=source_end
    )
    source_len = sum(
        [len(source_sentence.raw_text) for source_sentence in source_sentences]
    )
    source_word_len = sum(
        [
            len(source_sentence.preprocessed_text.split(","))
            for source_sentence in source_sentences
        ]
    )

    GivenPlagiarismCase.objects.create(
        sus_document=sus_doc,
        sus_start_sentence=sus_start,
        sus_end_sentence=sus_end,
        sus_length=sus_len,
        sus_word_len=sus_word_len,
        source_document=source_doc,
        source_start_sentence=source_start,
        source_end_sentence=source_end,
        source_length=source_len,
        source_word_len=source_word_len,
        obfuscation=obfuscation,
        type=type,
    )


def longest_consecutive_sentences(sentences):
    sequence_start = 0
    sequence_end = 0
    largest_sequence_start = 0
    largest_sequence_end = 0
    for i in range(1, len(sentences)):
        if sentences[i] == sentences[i - 1] + 1:
            if i == (len(sentences) - 1):
                sequence_end = i
                if (sequence_end - sequence_start + 1) > (
                    largest_sequence_end - largest_sequence_start + 1
                ):
                    largest_sequence_start = sequence_start
                    largest_sequence_end = sequence_end
            else:
                continue
        else:
            sequence_end = i - 1
            if (sequence_end - sequence_start + 1) > (
                largest_sequence_end - largest_sequence_start + 1
            ):
                largest_sequence_start = sequence_start
                largest_sequence_end = sequence_end
            sequence_start = i

    return sentences[largest_sequence_start], sentences[largest_sequence_end]


def get_target_sentences(file_number, type, part):
    if type == "source":
        sentences = Document.objects.get(doc_num=file_number).sentences
    else:
        sentences = SuspiciousDocument.objects.get(doc_num=file_number).sentences

    target_sentences = []
    for sentence in sentences.all():
        # if "lageolets, to my grea" in sentence.raw_text:
        if sentence.raw_text.strip() in part:
            target_sentences.append(sentence.number)

    return target_sentences


class Command(BaseCommand):
    help = "Populate database with given plagiarism cases from dataset."

    def handle(self, *args, **options):
        suspicious_doc_num = 10375
        case_num = 29
        plagiarised_parts = get_plagiarised_part(suspicious_doc_num)
        print(len(plagiarised_parts))
        plagiarised_part = plagiarised_parts[case_num]

        print("==============suspicious================")
        print(plagiarised_part[2])
        sus_target_sents = get_target_sentences(
            suspicious_doc_num, "suspicious", plagiarised_part[2]
        )
        print(sus_target_sents)
        # print("=====================================")
        # sus_start = 1055
        # sus_end = 1055
        # print(get_sentences(suspicious_doc_num, "suspicious", sus_start, sus_end))

        print("==============source================")
        print(plagiarised_part[3])
        source_target_sents = get_target_sentences(
            plagiarised_part[0], "source", plagiarised_part[3]
        )
        print(source_target_sents)
        # print("=====================================")
        # source_start = 63
        # source_end = 63
        # print(get_sentences(plagiarised_part[0], "source", source_start, source_end))

        # create_given_case(
        #     sus_doc_num=suspicious_doc_num,
        #     sus_start=sus_start,
        #     sus_end=sus_end,
        #     source_doc_num=plagiarised_part[0],
        #     source_start=source_start,
        #     source_end=source_end,
        #     obfuscation=plagiarised_part[1],
        #     type=plagiarised_part[4],
        # )

        # curpath = os.path.dirname(__file__)
        # with open(os.path.join(curpath, "./logs.txt"), "a") as log_file:
        #     for suspicious_doc_num in range(1, 11094):
        #         plagiarised_parts = get_plagiarised_part(suspicious_doc_num)
        #         # print(f"file {suspicious_doc_num}")
        #         # print(f"number of plagiarised parts: {len(plagiarised_parts)}")
        #
        #         for idx, plagiarised_part in enumerate(plagiarised_parts):
        #             # print(f"Case: {idx + 1}")
        #             sus_target_sents = get_target_sentences(
        #                 suspicious_doc_num, "suspicious", plagiarised_part[2]
        #             )
        #             if len(sus_target_sents) <= 0:
        #                 print(f"suspicious document: {suspicious_doc_num}")
        #                 print(f"case: {idx}")
        #                 print("")
        #                 continue
        #             sus_start, sus_end = longest_consecutive_sentences(sus_target_sents)
        #             sus_sent_num = sus_end - sus_start + 1
        #
        #             source_target_sents = get_target_sentences(
        #                 plagiarised_part[0], "source", plagiarised_part[3]
        #             )
        #             if len(source_target_sents) <= 0:
        #                 print(f"suspicious document: {suspicious_doc_num}")
        #                 print(f"case: {idx}")
        #                 print("")
        #                 continue
        #             source_start, source_end = longest_consecutive_sentences(
        #                 source_target_sents
        #             )
        #             source_sent_num = source_end - source_start + 1
        #
        #             if (
        #                 sus_sent_num <= 2
        #                 or source_sent_num <= 2
        #                 or abs(source_sent_num - sus_sent_num) > 10
        #             ):
        #                 log_file.write(f"suspicious document: {suspicious_doc_num}\n")
        #                 log_file.write(f"case: {idx}\n")
        #                 log_file.write("===============suspicious===============\n")
        #                 log_file.write(plagiarised_part[2])
        #                 log_file.write("\n==============================\n")
        #                 log_file.write(
        #                     get_sentences(
        #                         suspicious_doc_num,
        #                         "suspicious",
        #                         sus_start,
        #                         sus_end,
        #                     )
        #                 )
        #                 log_file.write("\n===============source===============\n")
        #                 log_file.write(plagiarised_part[3])
        #                 log_file.write("\n================================\n")
        #                 log_file.write(
        #                     get_sentences(
        #                         plagiarised_part[0],
        #                         "source",
        #                         source_start,
        #                         source_end,
        #                     )
        #                 )
        #                 log_file.write("\n\n")
        #
        #             create_given_case(
        #                 sus_doc_num=suspicious_doc_num,
        #                 sus_start=sus_start,
        #                 sus_end=sus_end,
        #                 source_doc_num=plagiarised_part[0],
        #                 source_start=source_start,
        #                 source_end=source_end,
        #                 obfuscation=plagiarised_part[1],
        #                 type=plagiarised_part[4],
        #             )
