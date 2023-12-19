from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from . import views

app_name = 'fishbread'
urlpatterns = [
    path('fishbread', views.fishbread_info),
    path('fishbread/<int:id>', views.fishbread_detail),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)