# gallery/views.py (update home view)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import MediaFile
from django.http import JsonResponse
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
