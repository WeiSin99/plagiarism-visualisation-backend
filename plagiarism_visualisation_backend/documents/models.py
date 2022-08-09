import json
from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True)
    doc_num = models.IntegerField(unique=True)
    language = models.CharField(max_length=15)
    raw_text = models.TextField()
    authors = models.TextField(null=True, blank=True)
    keywords = models.JSONField(null=True, blank=True)

    def plagiarism_score(self, sus_doc_nums):
        plagiarism_cases = self.given_plagiarism_cases.filter(
            sus_document__doc_num__in=sus_doc_nums
        ).values_list("source_length")
        plagiarised_part_length = sum([case[0] for case in plagiarism_cases])
        total_length = len(self.raw_text)
        return min(0.99, plagiarised_part_length / total_length)

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
    doc_num = models.IntegerField(unique=True)
    language = models.CharField(max_length=15)
    raw_text = models.TextField()
    authors = models.TextField(null=True, blank=True)
    keywords = models.JSONField(null=True, blank=True)

    def plagiarism_score(self):
        plagiarism_cases = self.given_plagiarism_cases.values_list("sus_length")
        plagiarised_part_length = sum([case[0] for case in plagiarism_cases])
        total_length = len(self.raw_text)
        return plagiarised_part_length / total_length

    def get_candidates(self):
        suspicious_keywords = json.loads(self.keywords)
        documents = Document.objects.filter(language="en").values_list(
            "doc_num", flat=True
        )

        candidates = []
        for doc_num in documents:
            document = Document.objects.get(doc_num=doc_num)
            source_keywords = json.loads(document.keywords)
            if len(set(source_keywords).intersection(set(suspicious_keywords))) > 4:
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

    class Meta:
        ordering = ["-doc_num"]

    def __str__(self):
        return self.title


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

    def __str__(self):
        return f"{self.sus_document.doc_num}, {self.sus_start_sentence}, {self.sus_end_sentence}, {self.source_document.doc_num}, {self.source_start_sentence}, {self.source_end_sentence}"
        # return f"{self.obfuscation}, {self.type}"
        # return f"{self.sus_length}, {self.sus_word_len}, {self.source_length}, {self.source_word_len}"
