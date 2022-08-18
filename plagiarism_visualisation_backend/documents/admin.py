from django.contrib import admin
from .models import (
    Document,
    Sentence,
    SuspiciousDocument,
    SuspiciousSentence,
    GivenPlagiarismCase,
    PlagiarismCase,
)

# Register your models here.
admin.site.register(Document)
admin.site.register(Sentence)
admin.site.register(SuspiciousDocument)
admin.site.register(SuspiciousSentence)
admin.site.register(GivenPlagiarismCase)
admin.site.register(PlagiarismCase)
