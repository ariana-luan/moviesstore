from django.contrib import admin
from django.urls import path
from django.db.models import Sum
from django.shortcuts import render
from cart.models import Item

# Register your models here.

def leaderboard_view(request):
    stats = (
        Item.objects
        .values('order__user__username')
        .annotate(order_movies=Sum('quantity'))
        .order_by('-order_movies')
    )
    return render(request, 'admin/leaderboard.html', {
        **admin.site.each_context(request),
        'stats': stats,
    })

_original_get_urls = admin.site.get_urls

def get_urls():
    custom_urls = [
        path('leaderboard/', admin.site.admin_view(leaderboard_view), name='leaderboard'),
    ]
    return custom_urls + _original_get_urls()

admin.site.get_urls = get_urls
