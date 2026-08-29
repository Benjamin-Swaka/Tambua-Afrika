from django.shortcuts import render, get_object_or_404
from .models import Comic

def index(request):
    comics = Comic.objects.all().order_by('-created_at')
    return render(request, 'comics/index.html', {'comics': comics})

def detail(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    return render(request, 'comics/detail.html', {'comic': comic})