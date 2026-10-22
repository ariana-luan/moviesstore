from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from cart.models import Item, Order
from movies.models import Movie



PURCHASERS = {
    'purchaser4': 4,
    'purchaser3': 3,
    'purchaser2': 2,
    'purchaser1': 1,
}

class Command(BaseCommand):
    help = 'Creates four users with 4,3,2,1 and 1 movies purchased'

    def handle(self, *args, **options):
        movie = Movie.objects.order_by('id').first()
        if movie is None:
            self.stdout.write(self.style.ERROR('No movies found. Add movies before seeding purchasers.'))
            return

        for username, purchase_count in PURCHASERS.items():
            user,_ = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'},
            )
            user.set_password('password123')
            user.is_staff = True
            user.save()

            Order.objects.filter(user=user).delete()
            order = Order.objects.create(
                total=movie.price * purchase_count,
                user=user,
            )
            Item.objects.create(
                price=movie.price,
                quantity=purchase_count,
                order=order,
                movie=movie,
            )

            self.stdout.write(self.style.SUCCESS(f'{username}: {purchase_count} movies purchased'))