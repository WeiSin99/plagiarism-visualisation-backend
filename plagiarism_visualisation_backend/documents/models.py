import json
import random
from django.db import models


def post_filter_plag_cases(plagCases):
    filtered_cases_ids = []
    for case in plagCases:
        word_difference_threshold = 0.2
        single_sentence_score_threshold = 0.975
        minimum_sentence_word_len = 4

        if (
            case.sus_word_len <= minimum_sentence_word_len
            or case.source_word_len <= minimum_sentence_word_len
        ):
            continue

        if (
            min(case.sus_word_len, case.source_word_len)
            / max(case.sus_word_len, case.source_word_len)
            > 1 - word_difference_threshold
        ):
            if (
                case.sus_end_sentence - case.sus_start_sentence == 0
                or case.source_end_sentence - case.source_start_sentence == 0
            ):
                if case.score > single_sentence_score_threshold:
                    filtered_cases_ids.append(case.id)
            else:
                filtered_cases_ids.append(case.id)

    return PlagiarismCase.objects.filter(id__in=filtered_cases_ids)


class Document(models.Model):
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True)
    doc_num = models.IntegerField(unique=True, db_index=True)
    language = models.CharField(max_length=15)
    raw_text = models.TextField()
    authors = models.TextField(null=True, blank=True)
    keywords = models.JSONField(null=True, blank=True)
    plagiarism_score = models.FloatField(null=True, blank=True)

    # def plagiarism_score(self):
    #     plagiarism_cases = self.detected_plagiarism_cases().values_list(
    #         "source_length", flat=True
    #     )
    #
    #     plagiarised_part_length = sum(plagiarism_cases)
    #     total_length = len(self.raw_text)
    #     return plagiarised_part_length / total_length

    def detected_plagiarism_cases(self):
        plagiarism_cases = self.plagiarism_cases.all()
        return post_filter_plag_cases(plagiarism_cases).order_by(
            "source_start_sentence"
        )

    def given_plagiarised_suspicious_document(self):
        sus_ids = (
            self.given_plagiarism_cases.order_by("sus_document")
            .values_list("sus_document")
            .distinct()
        )
        suspicious_documents = SuspiciousDocument.objects.filter(id__in=sus_ids)
        return [doc.doc_num for doc in suspicious_documents]

    def serialize(self):
        return {
            "title": self.title,
            "doc-num": self.doc_num,
            "authors": self.authors,
        }

    class Meta:
        ordering = ["-doc_num"]

    def __str__(self):
        return self.title


class Sentence(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="sentences"
    )
    raw_text = models.TextField()
    preprocessed_text = models.TextField(null=True, blank=True)
    number = models.IntegerField(db_index=True)

    def serialize(self):
        return {
            "number": self.number,
            "rawText": self.raw_text,
            "preprocessed-text": self.preprocessed_text,
        }

    def __str__(self):
        return self.raw_text

    class Meta:
        ordering = ["document", "number"]


class SuspiciousDocument(models.Model):
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True)
    doc_num = models.IntegerField(unique=True, db_index=True)
    language = models.CharField(max_length=15)
    raw_text = models.TextField()
    authors = models.TextField(null=True, blank=True)
    keywords = models.JSONField(null=True, blank=True)
    plagiarism_score = models.FloatField(null=True, blank=True)

    # def plagiarism_score(self):
    #     plagiarism_cases = self.detected_plagiarism_cases().values_list(
    #         "sus_length", flat=True
    #     )
    #
    #     plagiarised_part_length = sum(plagiarism_cases)
    #     total_length = len(self.raw_text)
    #     return plagiarised_part_length / total_length

    def detected_plagiarism_cases(self):
        plagiarism_cases = self.plagiarism_cases.all()
        return post_filter_plag_cases(plagiarism_cases).order_by("sus_start_sentence")

    def get_candidates(self):
        suspicious_keywords = json.loads(self.keywords)
        documents = Document.objects.filter(language="en").values_list(
            "doc_num", flat=True
        )

        candidates = []
        for doc_num in documents:
            document = Document.objects.get(doc_num=doc_num)
            source_keywords = json.loads(document.keywords)
            if len(set(source_keywords).intersection(set(suspicious_keywords))) > 1:
                candidates.append(doc_num)

        return candidates

    def given_plagiarised_source_document(self):
        source_ids = (
            self.given_plagiarism_cases.order_by("source_document")
            .values_list("source_document")
            .distinct()
        )
        source_documents = Document.objects.filter(id__in=source_ids)
        return [doc.doc_num for doc in source_documents]

    def serialize(self):
        return {
            "title": self.title,
            "doc-num": self.doc_num,
            "authors": self.authors,
        }

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-doc_num"]


class SuspiciousSentence(models.Model):
    document = models.ForeignKey(
        SuspiciousDocument, on_delete=models.CASCADE, related_name="sentences"
    )
    raw_text = models.TextField()
    preprocessed_text = models.TextField(null=True, blank=True)
    number = models.IntegerField(db_index=True)

    def serialize(self):
        return {
            "number": self.number,
            "rawText": self.raw_text,
            "preprocessed-text": self.preprocessed_text,
        }

    def __str__(self):
        return self.raw_text

    class Meta:
        ordering = ["document", "number"]


class GivenPlagiarismCase(models.Model):
    sus_document = models.ForeignKey(
        SuspiciousDocument,
        on_delete=models.CASCADE,
        related_name="given_plagiarism_cases",
    )
    sus_start_sentence = models.IntegerField()
    sus_end_sentence = models.IntegerField()
    sus_length = models.IntegerField()
    sus_word_len = models.IntegerField()

    source_document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="given_plagiarism_cases"
    )
    source_start_sentence = models.IntegerField()
    source_end_sentence = models.IntegerField()
    source_length = models.IntegerField()
    source_word_len = models.IntegerField()
    obfuscation = models.CharField(max_length=15, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)

    def serialize(self):
        return {
            "filenum": self.source_document.doc_num,
            "thisStart": self.sus_start_sentence,
            "thisEnd": self.sus_end_sentence,
            "thisLength": self.sus_length,
            "sourceStart": self.source_start_sentence,
            "sourceEnd": self.source_end_sentence,
            "sourceLength": self.source_length,
            "averageScore": random.randint(97, 100) / 100,
        }

    def __str__(self):
        return f"{self.sus_document.doc_num}, {self.sus_start_sentence}, {self.sus_end_sentence}, {self.source_document.doc_num}, {self.source_start_sentence}, {self.source_end_sentence}"
        # return f"{self.obfuscation}, {self.type}"
        # return f"{self.sus_length}, {self.sus_word_len}, {self.source_length}, {self.source_word_len}"


class PlagiarismCase(models.Model):
    sus_document = models.ForeignKey(
        SuspiciousDocument,
        on_delete=models.CASCADE,
        related_name="plagiarism_cases",
    )
    sus_start_sentence = models.IntegerField()
    sus_end_sentence = models.IntegerField()
    sus_length = models.IntegerField()
    sus_word_len = models.IntegerField()

    source_document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="plagiarism_cases"
    )
    source_start_sentence = models.IntegerField()
    source_end_sentence = models.IntegerField()
    source_length = models.IntegerField()
    source_word_len = models.IntegerField()
    score = models.FloatField(null=True, blank=True)

    def serialize(self, type):
        if type == "source":
            filenum = self.sus_document.doc_num
            this_start = self.source_start_sentence
            this_end = self.source_end_sentence
            this_length = self.source_length
            this_word_length = self.source_word_len
            source_start = self.sus_start_sentence
            source_end = self.sus_end_sentence
            source_length = self.sus_length
            source_word_length = self.sus_word_len
        elif type == "suspicious":
            filenum = self.source_document.doc_num
            this_start = self.sus_start_sentence
            this_end = self.sus_end_sentence
            this_length = self.sus_length
            this_word_length = self.sus_word_len
            source_start = self.source_start_sentence
            source_end = self.source_end_sentence
            source_length = self.source_length
            source_word_length = self.source_word_len
        else:
            return {}

        return {
            "filenum": filenum,
            "thisStart": this_start,
            "thisEnd": this_end,
            "thisLength": this_length,
            "thisWordLength": this_word_length,
            "sourceStart": source_start,
            "sourceEnd": source_end,
            "sourceLength": source_length,
            "sourceWordLength": source_word_length,
            "averageScore": self.score,
        }

    def __str__(self):
        return f"{self.sus_document.doc_num}, {self.sus_start_sentence}, {self.sus_end_sentence}, {self.source_document.doc_num}, {self.source_start_sentence}, {self.source_end_sentence}"
