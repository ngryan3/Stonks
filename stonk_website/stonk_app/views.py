from django.http import HttpResponse
from django.shortcuts import render
from .utils import *


from .forms import StonkForm

# Create your views here.
def home_view(request, *args, **kwargs):
    #return HttpResponse("<h1>Hello World</h1>") 
    return render(request, "home.html", {})

def portfolio_view(request, *args, **kwargs):
    form = StonkForm(request.POST or None)
    print(request.POST)
    
    print(form.is_valid())

    # Perform optimization algo if form is valid

    context = {
        'form': form
    }

    context['graph'] = demo_plot()
    
    
    return render(request, 'portfolio.html', context)

def about_view(request, *args, **kwargs):
    return render(request, 'about.html', {})


def limitations_view(request, *args, **kwargs):
    return render(request, 'limitations.html', {})