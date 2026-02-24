# gallery/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.upload, name="upload"),
    path("photos/", views.photos_list, name="photos_list"),
    path("videos/", views.videos_list, name="videos_list"),
    path("documents/", views.docs_list, name="docs_list"),
    path("delete/<int:pk>/", views.delete_file, name="delete_file"),
    path("media/<int:pk>/", views.media_detail, name="media_detail"),
    path("albums/", views.album_list, name="album_list"),
    path("albums/create/", views.album_create, name="album_create"),
    path("albums/<int:pk>/edit/", views.album_edit, name="album_edit"),
    path("albums/<int:pk>/delete/", views.album_delete, name="album_delete"),
    path("albums/<int:pk>/", views.album_detail, name="album_detail"),
    path(
        "albums/<int:album_pk>/add/<int:media_pk>/",
        views.add_to_album,
        name="add_to_album",
    ),
    path(
        "albums/<int:album_pk>/remove/<int:media_pk>/",
        views.remove_from_album,
        name="remove_from_album",
    ),
]
