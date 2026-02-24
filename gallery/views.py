# gallery/views.py (update home view)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from .forms import UploadForm, AlbumForm
from .models import MediaFile, Album


@login_required
def home(request):
    user_files = MediaFile.objects.filter(user=request.user)

    # Stats
    photos_count = user_files.filter(media_type="photo").count()
    videos_count = user_files.filter(media_type="video").count()
    docs_count = user_files.filter(media_type="document").count()
    total_size = user_files.aggregate(total=Sum("size"))["total"] or 0
    total_size_gb = round(total_size / (1024**3), 2)  # Bytes to GB

    # Recent uploads (last 12)
    recent_uploads = user_files.order_by("-uploaded_at")[:12]

    context = {
        "photos_count": photos_count,
        "videos_count": videos_count,
        "docs_count": docs_count,
        "total_size_gb": total_size_gb,
        "recent_uploads": recent_uploads,
    }
    return render(request, "gallery/home.html", context)


@login_required
def upload(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user  # Save to current user
            instance.save()
            if (
                request.headers.get("x-requested-with") == "XMLHttpRequest"
            ):  # AJAX response
                return JsonResponse({"success": True, "file_url": instance.file.url})
            return redirect("home")  # Normal redirect to dashboard
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )
    else:
        form = UploadForm()

    return render(request, "gallery/upload.html", {"form": form})


@login_required
def photos_list(request):
    queryset = MediaFile.objects.filter(
        user=request.user, media_type="photo", is_deleted=False
    )
    queryset = apply_filters(request, queryset)
    context = {"files": queryset, "title": "Photos", "type": "photo"}
    return render(request, "gallery/media_list.html", context)


@login_required
def videos_list(request):
    queryset = MediaFile.objects.filter(
        user=request.user, media_type="video", is_deleted=False
    )
    queryset = apply_filters(request, queryset)
    context = {"files": queryset, "title": "Videos", "type": "video"}
    return render(request, "gallery/media_list.html", context)


@login_required
def docs_list(request):
    queryset = MediaFile.objects.filter(
        user=request.user, media_type="document", is_deleted=False
    )
    queryset = apply_filters(request, queryset)
    context = {"files": queryset, "title": "Documents", "type": "document"}
    return render(request, "gallery/media_list.html", context)


def apply_filters(request, queryset):
    category = request.GET.get("category")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if category:
        queryset = queryset.filter(category=category)
    if start_date:
        queryset = queryset.filter(
            uploaded_at__gte=datetime.strptime(start_date, "%Y-%m-%d")
        )
    if end_date:
        queryset = queryset.filter(
            uploaded_at__lte=datetime.strptime(end_date, "%Y-%m-%d")
        )

    return queryset


@login_required
def delete_file(request, pk):
    file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    file.delete()  # Soft delete
    return redirect(request.GET.get("next", "home"))  # Redirect back to list or home


@login_required
def media_detail(request, pk):
    file = get_object_or_404(MediaFile, pk=pk, user=request.user, is_deleted=False)
    context = {"file": file}
    return render(request, "gallery/media_detail.html", context)


@login_required
def album_list(request):
    albums = Album.objects.filter(user=request.user)
    return render(request, "gallery/album_list.html", {"albums": albums})


# ====================== CREATE ALBUM ======================
@login_required
def album_create(request):
    if request.method == "POST":
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            return redirect("album_list")
    else:
        form = AlbumForm()
    return render(
        request, "gallery/album_form.html", {"form": form, "title": "Create New Album"}
    )


# ====================== EDIT / RENAME ALBUM ======================
@login_required
def album_edit(request, pk):
    album = get_object_or_404(Album, pk=pk, user=request.user)
    if request.method == "POST":
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            return redirect("album_list")
    else:
        form = AlbumForm(instance=album)
    return render(
        request, "gallery/album_form.html", {"form": form, "title": "Rename Album"}
    )


# ====================== DELETE ALBUM ======================
@login_required
def album_delete(request, pk):
    album = get_object_or_404(Album, pk=pk, user=request.user)
    album.delete()
    return redirect("album_list")


# ====================== ALBUM DETAIL (Media inside) ======================
@login_required
def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk, user=request.user)
    media_in_album = album.media_files.filter(is_deleted=False)

    # All user media not in this album (for "Add Media" dropdown)
    all_user_media = MediaFile.objects.filter(
        user=request.user, is_deleted=False
    ).exclude(albums=album)

    return render(
        request,
        "gallery/album_detail.html",
        {
            "album": album,
            "media_in_album": media_in_album,
            "all_user_media": all_user_media,
        },
    )


# ====================== ADD MEDIA TO ALBUM ======================
@login_required
def add_to_album(request, album_pk, media_pk):
    album = get_object_or_404(Album, pk=album_pk, user=request.user)
    media = get_object_or_404(MediaFile, pk=media_pk, user=request.user)

    album.media_files.add(media)

    # Set cover if album has no cover
    if not album.cover:
        album.cover = media
        album.save()

    return redirect("album_detail", pk=album_pk)


# ====================== REMOVE MEDIA FROM ALBUM ======================
@login_required
def remove_from_album(request, album_pk, media_pk):
    album = get_object_or_404(Album, pk=album_pk, user=request.user)
    media = get_object_or_404(MediaFile, pk=media_pk)
    album.media_files.remove(media)
    return redirect("album_detail", pk=album_pk)
