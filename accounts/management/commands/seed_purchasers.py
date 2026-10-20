import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from cart.models import Item, Order
from movies.models import Movie

# username -> number of movies to purchase (summed quantity across items)
PURCHASERS = {
    'alice': 7,
    'bob': 5,
    'carol': 5,
    'dave': 3,
    'erin': 2,
    'frank': 1,
}


class Command(BaseCommand):
    help = 'Seeds the database with users who have purchased movies, for the admin leaderboard.'

    def handle(self, *args, **options):
        movies = list(Movie.objects.all())
        if not movies:
            self.stdout.write(self.style.ERROR('No movies found. Add movies before seeding purchasers.'))
            return

        for username, movie_count in PURCHASERS.items():
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'},
            )
            if created:
                user.set_password('password123')
                user.save()

            remaining = movie_count
            while remaining > 0:
                movie = random.choice(movies)
                quantity = min(remaining, random.randint(1, 2))
                order = Order.objects.create(total=movie.price * quantity, user=user)
                Item.objects.create(
                    price=movie.price,
                    quantity=quantity,
                    order=order,
                    movie=movie,
                )
                remaining -= quantity

            self.stdout.write(self.style.SUCCESS(f'{username}: {movie_count} movies purchased'))
