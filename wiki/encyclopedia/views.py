from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import random

from markdown2 import Markdown

from . import util

to_md = Markdown()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry_content": to_md.convert(util.get_entry(title))
    })

def search(request):
    searched_entry = request.GET['q']
    entries = util.list_entries()
    num_entries = len(entries)
    
    similar_entries = []
    # Check is searched entry match fully or partially wit the
    # current entries
    for i in range(num_entries):
        # If match completely: return that entry
        if searched_entry.lower() == entries[i].lower():
            return entry(request, entries[i])
        # else create a list of entries that partially match
        elif searched_entry.lower() in entries[i].lower():
            similar_entries += [entries[i]]
    
    # Print the list of those entries that partially match
    if similar_entries:
        return render(request, "encyclopedia/search.html", {
            "similar_entries": similar_entries,
            "num_entries": len(similar_entries),
            "searched_entry": searched_entry,
            "match": True
        })
    
    # otherwise return search page  - not found
    return render(request, "encyclopedia/search.html", {
        "searched_entry": searched_entry,
        "match": False
    })

def create(request):
    if request.method == "POST":
        # If title already exist return error
        if request.POST['net'].lower() in list(map(util.to_lower, util.list_entries())):
            return render(request, "encyclopedia/error.html", {
                'error_title': "Title already exist",
            })
        # Create and return the title
        util.save_entry(request.POST['net'], request.POST['nec'])
        return entry(request, request.POST['net'])

    return render(request, "encyclopedia/create_entry.html")

def edit(request):
    """
    Edit and update existent pages.
    """
    if request.method == "POST":
        # Enter the changed content
        print(f"Post content: {request.POST}")
        # Save the changes to disk
        util.save_entry(request.POST['title'], request.POST['eec'])
        # Render the updated page
        return entry(request, request.POST['title'])

    # Render the to-edit page
    if request.GET['toedit'].lower() in list(map(util.to_lower, util.list_entries())):
        return render(request, "encyclopedia/edit_entry.html", {
            "entry_content": util.get_entry(request.GET['toedit']),
            "title": request.GET['toedit']
        })
    # When title not found return error message
    else:
        return render(request, "encyclopedia/error.html", {
            "error_title": "Something went wrong. The to-edit page not found :("
        })

def random_entry(request):
    # choose and render randomly an entry
    if request.method == "GET":
        entry = random.choice(util.list_entries())
        return HttpResponseRedirect(f"wiki/{entry}")
