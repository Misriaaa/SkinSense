# detector/urls.py
from django.urls import path
from . import views

app_name = "detector"

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.upload, name="upload"),
    path("result/", views.result, name="result"),  # optional direct view
    path("about/", views.about, name="about"),
]
