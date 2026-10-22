from django.contrib import admin
from .models import Order, Item
from movies.models import Movie, Review
from django.shortcuts import render
from django.urls import path

admin.site.register(Order)
admin.site.register(Item)
# Register your models here.

def top_movies(request):
    movies = Movie.objects.all()

    max_purchase_movie = ""
    max_purchases = 0
    max_review_movie = ""
    max_reviews = 0

    for movie in movies:
        purchase_count = Item.objects.filter(movie=movie).count()
        if purchase_count > max_purchases:
            max_purchases = purchase_count
            max_purchase_movie = movie.name

        review_count = Review.objects.filter(movie=movie).count()
        if review_count > max_reviews:
            max_reviews = review_count
            max_review_movie = movie.name

    template_data = {'title': "Top Movies", 'p_movie': max_purchase_movie, 'r_movie': max_review_movie}

    return render(request, 'cart/admin.html', {**admin.site.each_context(request), 'template_data': template_data})

        
        

def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            path('top_movies/', admin.site.admin_view(top_movies), name="top-movies")
        ]
        return my_urls + urls
    return get_urls


admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
