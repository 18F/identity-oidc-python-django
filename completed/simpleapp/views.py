from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    return render(request, "simpleapp.html")


@login_required
def protected(request):
    return render(request, "protected.html")

