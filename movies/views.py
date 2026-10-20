from django.db.models.aggregates import Avg
from django.shortcuts import render, redirect, get_object_or_404

from cart import models
from .models import Movie, Review, Ratings
from django.contrib.auth.decorators import login_required


# movies = [
#     {
#         'id': 1, 'name': 'Inception', 'price': 12,
#         'description': 'A mind-bending heist thriller.'
#     },
#     {
#         'id': 2, 'name': 'Avatar', 'price': 13,
#         'description': 'A journey to a distant world and the battle for resources.'
#     },
#     {
#         'id': 3, 'name': 'The Dark Knight', 'price': 14,
#         'description': 'Gothams vigilante faces the Joker.'
#     },
#     {
#         'id': 4, 'name': 'Titanic', 'price': 11,
#         'description': 'A love story set against the backdrop of the sinking Titanic.',
#     },
# ]


def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id = id)
    reviews = Review.objects.filter(movie = movie)
    average = Ratings.objects.filter(movie=movie).aggregate(Avg('stars'))['stars__avg']
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Ratings.objects.filter(movie=movie, user=request.user).first()
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['average'] = average
    template_data['user_rating'] = user_rating

    return render(request, 'movies/show.html', {'template_data': template_data})

def report_review(request, id, review_id):
    review = get_object_or_404(Review, id = review_id)
    #if (request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)


@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


@login_required
def rate_movie(request, id):
    if request.method == 'POST':
        movie = Movie.objects.get(id=id)
        stars = int(request.POST.get('stars', 0))
        if 1 <= stars <= 5:
            Ratings.objects.update_or_create(
                movie = movie,
                user = request.user,
                defaults = {'stars': stars}
            )
    return redirect('movies.show', id=id)
