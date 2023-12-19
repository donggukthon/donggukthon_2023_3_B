from django.urls import path
from .views import *
from . import views

app_name = 'charity'
urlpatterns = [
    path('charity', views.charity_list),
    path('charity/<int:id>', views.charity_detail),
]