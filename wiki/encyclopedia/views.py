from django.shortcuts import render
from django.http import HttpResponse

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry_content": util.get_entry(title)
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
