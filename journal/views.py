from django.shortcuts import render, get_object_or_404
from .models import Article

def index(request):
    # Get latest 3 articles for hero, rest for grid
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'journal/index.html', {'articles': articles})

def detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'journal/detail.html', {'article': article})