from django.contrib import admin
from .models import User, Category, ListingObject, Bid, Comment
# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(ListingObject)
admin.site.register(Bid)
admin.site.register(Comment)