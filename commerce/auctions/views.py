from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Category, ListingObject, Bid, Comment,Whatchlist


def index(request):
    # Get available listing and bids
    listings = ListingObject.objects.all()
    bids = Bid.objects.all()

    # number watchlist elements
    nwe = len(Whatchlist.objects.filter(user=request.user.pk))
    
    return render(request, "auctions/index.html", {
        'listings': listings,
        'bids': bids,
        'nwe': nwe
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

@login_required(login_url='login')
def new_listing(request):
    # get all available categories
    categories = Category.objects.all()

    # number watchlist elements
    nwe = len(Whatchlist.objects.filter(user=request.user.pk))

    return render(request, "auctions/create.html", {
        'categories': categories,
        'nwe': nwe
    })

@login_required(login_url='login')
def add_new(request):
    # Save new listing info
    if request.method == "POST":
        # Get the form data
        name = request.POST["listing-title"]
        details = request.POST["listing-description"]
        price = request.POST["listing-initial-bid"]
        status = request.POST["status"]
        image_url = request.POST["listing-image"]

        # Generate instances to reference as foregin key values
        current_user = User.objects.get(pk=request.user.pk)
        current_category = Category.objects.get(pk=request.POST["category-list"])

        # Create a new listing object
        listing_object = ListingObject(
            name=name,
            category=current_category, # Reference an instance not a number/string
            user=current_user, # Reference an instance not a number/string
            details=details,
            image_url=image_url,
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
    listing_bids = list(Bid.objects.filter(listing_obj=listing_current))

    # number of bids
    number_bids = len(listing_bids)
    # get the current bid
    for bid in listing_bids:
        if bid.is_current:
            current_bid = bid
            break
    
    # Current status of the listing
    if listing_current.status == 'active':
        listing_status = 'active'
    elif listing_current.status == 'closed':
        listing_status = 'closed'
    else:
        listing_status = ''

    # Get watchlist info
    watchlist_list = list(Whatchlist.objects.filter(user=request.user.pk))
    # Check if current listing object was added to watchlist
    in_watchlist = False
    for e in watchlist_list:
        if e.listing_obj.id == listing_id:
            in_watchlist = True
            break
    
    # Get if current user is equal to owner listing page
    owner_equal_user = request.user.pk == listing_current.user.id

    # number of watchlist elements
    nwe = len(Whatchlist.objects.filter(user=request.user.pk))

    # Current user in session
    current_user = request.user.pk

    # Render the page with tue current listing info
    return render(request, "auctions/listing_page.html", {
        'listing_current': listing_current,
        'listing_bids': listing_bids,
        'number_bids': number_bids,
        'current_bid': current_bid,
        'listing_status': listing_status,
        'owner_equal_user': owner_equal_user,
        'current_user': current_user,
        'in_watchlist': in_watchlist,
        'nwe': nwe
    })

def close_listing(request, listing_id):
    if request.method == "POST":
        # Change the current listing object to closed
        listing_current = get_object_or_404(ListingObject, pk=listing_id)
        listing_current.status = "closed"
        listing_current.save()

        return HttpResponseRedirect(reverse('listing_page', args=(listing_id,)))

@login_required(login_url='login')
def place_bid(request, owner_id, listing_id):
    if request.method == "POST":
        bid_proposal = request.POST['bid']

        # Get current listing object
        listing_current = get_object_or_404(ListingObject, pk=listing_id)
        user_bid = User.objects.get(pk=request.user.pk)
        
        # find all bids made to that listing before
        listing_bids = list(Bid.objects.filter(listing_obj=listing_current))
        print(listing_bids)

        # check if current bid is higher than all the others
        for bid in listing_bids:
            if not bid.value or bid.value >= float(bid_proposal):
                messages.error(request, "You need a <strong>higher bid price</strong>.")
                return HttpResponseRedirect(reverse('listing_page', args=(listing_id,)))

        # check that bidder and owner are different users
        if request.user.pk == owner_id:
            messages.error(request, "You <strong>can't</strong> bid on <strong>your own</strong> listings.")
            return HttpResponseRedirect(reverse('listing_page', args=(listing_id,)))

        # set all the previous is_current bids to false
        for bid in listing_bids:
            bid.is_current = False
            bid.save()

        # add a new bid with the new info and set to true
        new_bid = Bid(
            user=user_bid,
            listing_obj=listing_current,
            value=bid_proposal,
            is_current=True
        )
        new_bid.save()
        
        # render the listing page with the new info
        messages.success(request, "Your bid was submitted correctly!")
        return HttpResponseRedirect(reverse('listing_page', args=(listing_id,)))
    
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url='login')
def add_watchlist(request, listing_id):
    if request.method == "POST":
        # Get current listing and user objects
        listing_current = get_object_or_404(ListingObject, pk=listing_id)
        user_current = get_object_or_404(User, pk=request.user.pk)

        # Create a new watchlist object and assign current objects
        watchlist_new=Whatchlist(
            user=user_current,
            listing_obj=listing_current
        )
        # save the new wathclist object
        watchlist_new.save()


        return HttpResponseRedirect(reverse('listing_page', args=(listing_id,)))

@login_required(login_url='login')
def watchlist(request):
    # get watchlist objects of current user
    user_watchlist_objects = list(Whatchlist.objects.filter(user=request.user.pk))

    # number of watchlist elements
    nwe = len(Whatchlist.objects.filter(user=request.user.pk))

    # render watchlist view
    return render(request, "auctions/watchlist.html", {
        "user_watchlist_objects": user_watchlist_objects,
        'nwe': nwe
    })

@login_required(login_url='login')
def remove_watchlist(request, listing_id):
    if request.method == "POST":
        # get watchlist objects related to the current user
        watchlist_user_objects = Whatchlist.objects.filter(user=request.user.pk)
        # remove from DB listing_id object
        print(watchlist_user_objects)
        for obj in watchlist_user_objects:
            if obj.listing_obj.id == listing_id:
                obj.delete()
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
