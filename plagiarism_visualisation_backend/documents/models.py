from django.db import models


class Document(models.Model):
    DOCUMENT_TYPE = [
        ("source", "source"),
        ("suspicious", "suspicious"),
    ]

    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True)
    doc_num = models.IntegerField(unique=True)
    type = models.CharField(max_length=15, choices=DOCUMENT_TYPE)
    language = models.CharField(max_length=15)
    raw_text = models.TextField()

    class Meta:
        ordering = ["-doc_num"]

    def __str__(self):
        return self.title


class Sentence(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="sentences"
    )
    raw_text = models.TextField()
    number = models.IntegerField()

    def __str__(self):
        return self.raw_text

    class Meta:
        ordering = ["document", "number"]


class Author(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    document = models.ManyToManyField(Document, related_name="authors", blank=True)

    def __str__(self):
        return self.name


class SuspiciousDocument(models.Model):
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True)
    doc_num = models.IntegerField(unique=True)
    language = models.CharField(max_length=15)
    raw_text = models.TextField()

    class Meta:
        ordering = ["-doc_num"]

    def __str__(self):
        return self.title


class SuspiciousSentence(models.Model):
    document = models.ForeignKey(
        SuspiciousDocument, on_delete=models.CASCADE, related_name="sentences"
    )
    raw_text = models.TextField()
    number = models.IntegerField()

    def __str__(self):
        return self.raw_text

    class Meta:
        ordering = ["document", "number"]
