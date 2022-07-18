from django.contrib import admin
from .models import Document, Sentence, Author, SuspiciousDocument, SuspiciousSentence

# Register your models here.
admin.site.register(Document)
admin.site.register(Sentence)
admin.site.register(Author)
admin.site.register(SuspiciousDocument)
admin.site.register(SuspiciousSentence)
