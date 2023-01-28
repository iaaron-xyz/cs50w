from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
class Category(models.Model):
    category = models.CharField(max_length=64)
class ListingObject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="obj_user")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="categories")
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=500)
    status = models.CharField(max_length=100)
    image_url = models.URLField(max_length=300)
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user")
    listing_obj = models.ForeignKey(ListingObject, on_delete=models.CASCADE, related_name="bid_obj")
    value = models.DecimalField(max_digits=11, decimal_places=2)
    is_current = models.BooleanField(default=False)
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    listing_obj = models.ForeignKey(ListingObject, on_delete=models.CASCADE, related_name="comment_obj")
    comment_text = models.CharField(max_length=2000)

class whatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_user")
    listing_obj = models.ForeignKey(ListingObject, on_delete=models.CASCADE, related_name="watch_obj")