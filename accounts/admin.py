from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, IntegerField, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.urls import path

from cart.models import Item
from movies.models import Review

# Register your models here.
def purchase_ranking_view(request):
    stats = (
        User.objects
        .annotate(
            purchase_count=Coalesce(
                Sum('order__item__quantity'),
                Value(0),
                output_field=IntegerField(),
            )
        )
        .order_by('-purchase_count', 'username')
    )

    limit_raw = request.GET.get('limit', '').strip()
    limit = ''
    limit_error = ''
    if limit_raw:
        try:
            parsed_limit = int(limit_raw)
        except ValueError:
            parsed_limit = None
        if parsed_limit is not None and parsed_limit > 0:
            limit = parsed_limit
            stats = stats[:parsed_limit]
        else:
            limit_error = (
                'List size must be a positive integer. '
                'Showing all users.'
            )

    return render(request, 'admin/purchase_ranking.html', {
        **admin.site.each_context(request),
        'title': 'Purchase Ranking',
        'stats': stats,
        'limit': limit,
        'limit_error': limit_error,
    })

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
        path('purchase-ranking/', admin.site.admin_view(purchase_ranking_view), name='purchase_ranking'),
    ]
    return custom_urls + _original_get_urls()

admin.site.get_urls = get_urls
