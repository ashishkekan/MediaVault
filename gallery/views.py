# gallery/views.py (update home view)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import MediaFile
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from .forms import UploadForm

@login_required
def home(request):
    user_files = MediaFile.objects.filter(user=request.user)
    
    # Stats
    photos_count = user_files.filter(media_type='photo').count()
    videos_count = user_files.filter(media_type='video').count()
    docs_count = user_files.filter(media_type='document').count()
    total_size = user_files.aggregate(total=Sum('size'))['total'] or 0
    total_size_gb = round(total_size / (1024 ** 3), 2)  # Bytes to GB
    
    # Recent uploads (last 12)
    recent_uploads = user_files.order_by('-uploaded_at')[:12]
    
    context = {
        'photos_count': photos_count,
        'videos_count': videos_count,
        'docs_count': docs_count,
        'total_size_gb': total_size_gb,
        'recent_uploads': recent_uploads,
    }
    return render(request, 'gallery/home.html', context)


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user  # Save to current user
            instance.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX response
                return JsonResponse({'success': True, 'file_url': instance.file.url})
            return redirect('home')  # Normal redirect to dashboard
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = UploadForm()
    
    return render(request, 'gallery/upload.html', {'form': form})


@login_required
def photos_list(request):
    queryset = MediaFile.objects.filter(user=request.user, media_type='photo', is_deleted=False)
    queryset = apply_filters(request, queryset)
    context = {'files': queryset, 'title': 'Photos', 'type': 'photo'}
    return render(request, 'gallery/media_list.html', context)

@login_required
def videos_list(request):
    queryset = MediaFile.objects.filter(user=request.user, media_type='video', is_deleted=False)
    queryset = apply_filters(request, queryset)
    context = {'files': queryset, 'title': 'Videos', 'type': 'video'}
    return render(request, 'gallery/media_list.html', context)

@login_required
def docs_list(request):
    queryset = MediaFile.objects.filter(user=request.user, media_type='document', is_deleted=False)
    queryset = apply_filters(request, queryset)
    context = {'files': queryset, 'title': 'Documents', 'type': 'document'}
    return render(request, 'gallery/media_list.html', context)

def apply_filters(request, queryset):
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if category:
        queryset = queryset.filter(category=category)
    if start_date:
        queryset = queryset.filter(uploaded_at__gte=datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        queryset = queryset.filter(uploaded_at__lte=datetime.strptime(end_date, '%Y-%m-%d'))
    
    return queryset

@login_required
def delete_file(request, pk):
    file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    file.delete()  # Soft delete
    return redirect(request.GET.get('next', 'home'))  # Redirect back to list or home

@login_required
def media_detail(request, pk):
    file = get_object_or_404(MediaFile, pk=pk, user=request.user, is_deleted=False)
    context = {'file': file}
    return render(request, 'gallery/media_detail.html', context)