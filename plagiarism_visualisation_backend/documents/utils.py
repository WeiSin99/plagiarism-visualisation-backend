from .models import SuspiciousDocument, Document, PlagiarismCase


def intersection(start1, end1, start2, end2):
    intersection = range(
        max(start1, start2),
        min(end1, end2) + 1,
    )
    return list(intersection)


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


def filter_sentence(all_sus_sentences, sentence_number):
    sents_word_len = len(
        all_sus_sentences.get(number=sentence_number).preprocessed_text.split(",")
    )
    return sents_word_len


def merge_cases(sus_doc_num, potential_plagiarised_sents, window=2):
    all_sus_sentences = SuspiciousDocument.objects.get(doc_num=sus_doc_num).sentences
    potential_plagiarised_sents = [
        sent
        for sent in potential_plagiarised_sents
        if filter_sentence(all_sus_sentences, sent["suspicious_sentence_number"]) > 2
    ]
    if len(potential_plagiarised_sents) == 0:
        return []

    merged_suspicious_parts, _ = merge_sentences(potential_plagiarised_sents, window=3)

    merged_cases = []
    for part in merged_suspicious_parts:
        sorted_part = sorted(part, key=lambda x: x["source_sentence_number"])
        merged_source_parts, _ = merge_sentences(
            sorted_part, window, key="source_sentence_number"
        )
        # merged_cases = merged_source_parts
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

    merged_cases = sorted(merged_cases, key=lambda x: x["thisStart"])
    merged_cases = list(filter(lambda c: c["thisNumWords"] != 1, merged_cases))
    return merged_cases


def within_range(case, merged_cases):
    for i, merged_case in enumerate(merged_cases):
        if (
            case["thisStart"] >= merged_case["thisStart"]
            and case["thisEnd"] <= merged_case["thisEnd"]
        ):
            return i

    return -1


def case_within_range(case, merged_cases):
    for i, merged_case in enumerate(merged_cases):
        if (
            merged_case["thisStart"] >= case["thisStart"]
            and merged_case["thisEnd"] <= case["thisEnd"]
        ):
            return i

    return -1


def overlapped_range(case, merged_cases):
    for i, merged_case in enumerate(merged_cases):
        intersection = range(
            max(case["thisStart"], merged_case["thisStart"]),
            min(case["thisEnd"], merged_case["thisEnd"]) + 1,
        )
        if len(intersection) > 0:
            return i, list(intersection)

    return -1, []


def create_plagiarism_case(
    sus_doc_num,
    sus_start,
    sus_end,
    source_doc_num,
    source_start,
    source_end,
    score,
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

    PlagiarismCase.objects.create(
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
        score=score,
    )
