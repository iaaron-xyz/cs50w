from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
class Category(models.Model):
    category = models.CharField(max_length=100)
class ListingObject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Seller")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="listing category")
    name = models.CharField(max_length=200)
    details = models.CharField(max_length=500)
    status = models.CharField(max_length=100)
    image_url = models.URLField(max_length=300)
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="User bidder")
    listing_obj = models.ForeignKey(ListingObject, on_delete=models.CASCADE, related_name="Listing object bid")
    value = models.DecimalField(max_digits=11, decimal_places=2)
    is_current = models.BooleanField(default=False)
class Comment(models.Model):
    user = models.ForeignKey(User, on_Delete=models.CASCADE, related_name="User comment")
    listing_obj = models.ForeignKey(ListingObject, on_delete=models.CASCADE, related_name="Listing object comment")
    comment_text = models.CharField(max_length=2000)

class whatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="User watchlist")
    listing_obj = models.ForeignKey(ListingObject, on_delete=models.CASCADE, related_name="Listing object watchlist")