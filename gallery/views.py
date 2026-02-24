# gallery/views.py

from django.shortcuts import render


def home(request):
    return render(request, "gallery/home.html")  # Baad mein banaayenge
