# gallery/views.py (update home view)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import MediaFile

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
