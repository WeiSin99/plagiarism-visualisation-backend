from .models import SuspiciousDocument, Document


def assign_sentence_number(paragraph_reference, db_sentences, type, doc_num):
    processed_paragraphs = []
    sentence_number = 0
    for paragraph in paragraph_reference:
        processed_paragraph = []
        for sentence in paragraph:
            # quick fix for edge cases
            if type == "source" and doc_num == 5915 and sentence.strip() == ".  .  .":
                sentence = ".  ."
            if (
                type == "source"
                and doc_num == 5915
                and sentence.strip()
                == '"Not by multiplying clothes shall you make your body sound and healthy, but rather by discarding\nthem .  .  .'
            ):
                sentence = '"Not by multiplying clothes shall you make your body sound and healthy, but rather by discarding\nthem .'

            if (
                sentence == db_sentences[sentence_number]["rawText"]
                or db_sentences[sentence_number]["rawText"] in sentence
            ):
                processed_paragraph.append(
                    {"number": sentence_number, "rawText": sentence}
                )
                sentence_number += 1
            elif sentence.strip() in db_sentences[sentence_number]["rawText"]:
                processed_paragraph.append(
                    {"number": sentence_number, "rawText": sentence}
                )
            else:
                sentence_number += 1
                # print(sentence_number)
                # print(sentence.strip())
                # print("")
                while not (
                    sentence.strip() in db_sentences[sentence_number]["rawText"]
                    or db_sentences[sentence_number]["rawText"] in sentence
                ):
                    sentence_number += 1

                processed_paragraph.append(
                    {"number": sentence_number, "rawText": sentence}
                )
                if (
                    sentence == db_sentences[sentence_number]["rawText"]
                    or db_sentences[sentence_number]["rawText"] in sentence
                ):
                    sentence_number += 1

        processed_paragraphs.append(processed_paragraph)

    return processed_paragraphs


def merge_sentences(arr, window=2, key="suspicious_sentence_number"):
    if len(arr) < 2:
        return [arr], [[]]

    start = 0
    end = 1
    merge_arr = []
    merge_at = []
    while end < len(arr):
        if arr[end][key] - arr[end - 1][key] <= window + 1 and end != len(arr) - 1:
            end = end + 1
            continue

        if end == len(arr) - 1:
            if arr[end][key] - arr[end - 1][key] <= window + 1:
                merge_at.append([start, end + 1])
                merge_arr.append(arr[start : end + 1])
            else:
                merge_at.append([start, end])
                merge_arr.append(arr[start:end])
                merge_at.append([end, end + 1])
                merge_arr.append(arr[end : end + 1])
        else:
            merge_at.append([start, end])
            merge_arr.append(arr[start:end])
            start = end

        end = end + 1

    return merge_arr, merge_at


def merge_source_sentences(arr, merge_idx, window=2):
    merged_case = []
    for idx in merge_idx:
        merged_case.append(arr[idx[0] : idx[1]])

    merged_sentences = []
    for case in merged_case:
        sentence = sorted(case, key=lambda x: x["source_sentence_number"])
        merged_sentence, _ = merge_sentences(
            sentence, window, key="source_sentence_number"
        )
        merged_sentences.append(merged_sentence)

    return merged_sentences


def merge_cases(sus_doc_num, potential_plagiarised_sents, window=2):
    if len(potential_plagiarised_sents) == 0:
        return []

    merged_suspicious_parts, _ = merge_sentences(potential_plagiarised_sents, window=3)

    merged_cases = []
    for part in merged_suspicious_parts:
        sorted_part = sorted(part, key=lambda x: x["source_sentence_number"])
        merged_source_parts, _ = merge_sentences(
            sorted_part, window, key="source_sentence_number"
        )
        for source_part in merged_source_parts:
            this_start = min(
                source_part, key=lambda x: x["suspicious_sentence_number"]
            )["suspicious_sentence_number"]
            this_end = max(source_part, key=lambda x: x["suspicious_sentence_number"])[
                "suspicious_sentence_number"
            ]
            plagiarised_sentences = SuspiciousDocument.objects.get(
                doc_num=sus_doc_num
            ).sentences.filter(
                number__gte=this_start,
                number__lte=this_end,
            )
            this_char_length = sum(
                [len(sentence.raw_text) for sentence in plagiarised_sentences]
            )
            this_word_length = sum(
                [
                    len(sentence.preprocessed_text.split(","))
                    for sentence in plagiarised_sentences
                ]
            )

            source_start = min(source_part, key=lambda x: x["source_sentence_number"])[
                "source_sentence_number"
            ]
            source_end = max(source_part, key=lambda x: x["source_sentence_number"])[
                "source_sentence_number"
            ]
            source_sentences = Document.objects.get(
                doc_num=source_part[0]["filenum"]
            ).sentences.filter(
                number__gte=source_start,
                number__lte=source_end,
            )
            source_char_length = sum(
                [len(sentence.raw_text) for sentence in source_sentences]
            )
            source_word_length = sum(
                [
                    len(sentence.preprocessed_text.split(","))
                    for sentence in source_sentences
                ]
            )

            merged_cases.append(
                {
                    "filenum": source_part[0]["filenum"],
                    "thisStart": this_start,
                    "thisEnd": this_end,
                    "thisLength": this_char_length,
                    "thisNumWords": this_word_length,
                    "sourceStart": source_start,
                    "sourceEnd": source_end,
                    "sourceLength": source_char_length,
                    "sourceNumWords": source_word_length,
                    "averageScore": sum([sent["score"] for sent in source_part])
                    / len(source_part),
                }
            )

    return merged_cases
