from django.shortcuts import render
from .models import Post


def home(request):
    posts = Post.objects.all()[:5]
    context = {
        'posts': posts,
        'site_name': 'Django Starter'
    }
    return render(request, 'index.html', context)


def about(request):
    return render(request, 'about.html')
