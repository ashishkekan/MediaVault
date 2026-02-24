# gallery/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('upload/', views.upload, name='upload'),
    path('photos/', views.photos_list, name='photos_list'),
    path('videos/', views.videos_list, name='videos_list'),
    path('documents/', views.docs_list, name='docs_list'),
    path('delete/<int:pk>/', views.delete_file, name='delete_file'),
    path('media/<int:pk>/', views.media_detail, name='media_detail'),
]
