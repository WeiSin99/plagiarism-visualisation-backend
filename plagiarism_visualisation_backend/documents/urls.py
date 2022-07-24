from django.urls import path
from .views import detail_analysis

urlpatterns = [
    path("detail/<int:filenum>", detail_analysis, name="detail_analysis"),
]
