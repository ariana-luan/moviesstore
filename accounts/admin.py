from django.contrib import admin
from django.urls import path
from django.db.models import Sum, Count
from django.shortcuts import render
from cart.models import Item
from movies.models import Review

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

def comment_leaderboard_view(request):
    stats = list(
        Review.objects
        .values('user__username')
        .annotate(comment_count=Count('id'))
        .order_by('-comment_count', 'user__username')
    )

    leaders = []
    if stats:
        highest_count = stats[0]['comment_count']
        leaders = [
            row for row in stats if row['comment_count'] == highest_count
        ]

    return render(request, 'admin/comment_leaderboard.html', {
        **admin.site.each_context(request),
        'title': 'Top Commenters',
        'stats': stats,
        'leaders': leaders,
    })

_original_get_urls = admin.site.get_urls

def get_urls():
    custom_urls = [
        path('leaderboard/', admin.site.admin_view(leaderboard_view), name='leaderboard'),
        path('comment-leaderboard/', admin.site.admin_view(comment_leaderboard_view), name='comment_leaderboard'),
    ]
    return custom_urls + _original_get_urls()

admin.site.get_urls = get_urls
