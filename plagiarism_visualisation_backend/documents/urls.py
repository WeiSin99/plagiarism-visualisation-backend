from django.urls import path
from .views import (
    detail_analysis,
    suspicious_document_detail,
    source_document_detail,
    corpus_view,
)

urlpatterns = [
    path("detail/<str:type>/<int:filenum>", detail_analysis, name="detail_analysis"),
    path("corpus/<int:corpus_num>", corpus_view, name="corpus_view"),
    path(
        "suspicious-document/<int:filenum>",
        suspicious_document_detail,
        name="suspicious_document_detail",
    ),
    path(
        "source-document/<int:filenum>",
        source_document_detail,
        name="source_document_detail",
    ),
]
