from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, ListingObject, Bid


def index(request):
    # Get available listing and bids
    listings = ListingObject.objects.all()
    bids = Bid.objects.all()
    
    return render(request, "auctions/index.html", {
        'listings': listings,
        'bids': bids
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def new_listing(request):
    # get all available categories
    categories = Category.objects.all()
    return render(request, "auctions/create.html", {
        'categories': categories
    })

def add_new(request):
    # Save new listing info
    if request.method == "POST":
        # Get the form data
        name = request.POST["listing-title"]
        details = request.POST["listing-description"]
        price = request.POST["listing-initial-bid"]
        status = request.POST["status"]

        # Generate instances to reference as foregin key values
        current_user = User.objects.get(pk=request.user.pk)
        current_category = Category.objects.get(pk=request.POST["category-list"])

        # Create a new listing object
        listing_object = ListingObject(
            name=name,
            category=current_category, # Reference an instance not a number/string
            user=current_user, # Reference an instance not a number/string
            details=details,
            status=status)
        # save current listing to database
        listing_object.save()

        # Create bid new row
        bid = Bid(
            user=current_user, # Reference an instance not a number/string
            listing_obj=listing_object, # Reference an instance not a number/string
            value=price,
            is_current=True
        )
        # Save current bid to database
        bid.save()
        # Redirect to index after process to database
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return HttpResponseRedirect(reverse("new_listing"))

@login_required(login_url='login')
def listing_page(request, listing_id):
    # Get the info of the current listing object
    listing_current = get_object_or_404(ListingObject, pk=listing_id)
    
    # Just active listings can have a listing page
    is_active = True
    if listing_current.status != 'active' or  not listing_current:
        is_active = False

    # Render the page with tue current listing info
    return render(request, "auctions/listing_page.html", {
        'listing_current': listing_current,
        'is_active': is_active
    })