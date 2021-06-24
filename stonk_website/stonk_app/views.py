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
    stocks = None
    crypto = None
    print(form.errors.as_json())

    if request.method == 'POST' and form.is_valid():
        stocks = form.cleaned_data['stocks']
        crypto = form.cleaned_data['crypto_stocks']
        form = StonkForm()

    # Perform optimization algo if form is valid
    context = {
        'form': form,
        'stonks': stocks,
        'crypto': crypto
    }

    print(stocks, crypto)

    

    #context['graph'] = demo_plot()
    
    
    return render(request, 'portfolio.html', context)

def about_view(request, *args, **kwargs):
    return render(request, 'about.html', {})


def limitations_view(request, *args, **kwargs):
    return render(request, 'limitations.html', {})