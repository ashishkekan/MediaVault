# gallery/views.py (update home view)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from .forms import UploadForm, AlbumForm
from .models import MediaFile, Album
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator


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
    type_counts = (
        MediaFile.objects.filter(user=request.user, is_deleted=False)
        .values("media_type")
        .annotate(count=Count("id"))
    )

    context = {
        "photos_count": photos_count,
        "videos_count": videos_count,
        "docs_count": docs_count,
        "total_size_gb": total_size_gb,
        "recent_uploads": recent_uploads,
        "type_counts": {item["media_type"]: item["count"] for item in type_counts},
    }
    return render(request, "gallery/home.html", context)


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.user = request.user
            media.save()  # ← yaha category bhi save ho jayegi
            return redirect('home')
    else:
        form = UploadForm()

    return render(request, 'gallery/upload.html', {'form': form})


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


# ====================== GLOBAL SEARCH (Phase 8) ======================


@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()
    media_type = request.GET.get("type")
    category = request.GET.get("category")
    favorite_only = request.GET.get("favorite") == "1"
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    results = MediaFile.objects.filter(user=request.user, is_deleted=False)

    if query:
        results = results.filter(
            Q(file__icontains=query)
            | Q(tags__icontains=query)
            | Q(category__icontains=query)
        )
    if media_type:
        results = results.filter(media_type=media_type)
    if category:
        results = results.filter(category=category)
    if favorite_only:
        results = results.filter(is_favorite=True)
    if start_date:
        results = results.filter(uploaded_at__gte=start_date)
    if end_date:
        results = results.filter(uploaded_at__lte=end_date)

    # Pagination for Load More
    paginator = Paginator(results, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "results": page_obj,
        "query": query,
        "media_type": media_type,
        "category": category,
        "favorite_only": favorite_only,
        "start_date": start_date,
        "end_date": end_date,
        "has_next": page_obj.has_next(),
    }
    return render(request, "gallery/search.html", context)


# ====================== FAVORITE TOGGLE ======================
@login_required
def toggle_favorite(request, pk):
    file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    file.is_favorite = not file.is_favorite
    file.save()
    return JsonResponse({"is_favorite": file.is_favorite})


# ====================== TRASH BIN ======================
@login_required
def trash_bin(request):
    trash_files = MediaFile.objects.filter(user=request.user, is_deleted=True)
    return render(request, "gallery/trash.html", {"files": trash_files})


@login_required
def restore_file(request, pk):
    file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    file.is_deleted = False
    file.save()
    return redirect("trash_bin")


# ====================== DARK MODE TOGGLE ======================
@login_required
def toggle_dark_mode(request):
    current = request.session.get("theme", "dark")
    new_theme = "light" if current == "dark" else "dark"
    request.session["theme"] = new_theme
    return JsonResponse({"theme": new_theme})


@login_required
def share_link(request, pk):
    file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    share_url = request.build_absolute_uri(f"/share/{file.share_token}/")
    return JsonResponse({"share_url": share_url})


def public_share(request, token):
    file = get_object_or_404(MediaFile, share_token=token)
    return render(request, "gallery/public_share.html", {"file": file})
