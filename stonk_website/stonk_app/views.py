from django.http import HttpResponse
from django.shortcuts import render
from .utils.algo import *


from .forms import StonkForm

# Create your views here.
def home_view(request, *args, **kwargs):
    #return HttpResponse("<h1>Hello World</h1>") 
    return render(request, "home.html", {})

def portfolio_view(request, *args, **kwargs):
    form = StonkForm(request.POST or None)
    stocks = None
    crypto = None
    myplot = None
    port1_table = None
    port2_table = None

    if request.method == 'POST' and form.is_valid():
        stocks, stocks_list = form.cleaned_data['stocks']
        crypto, crypto_list = form.cleaned_data['crypto_stocks']
        t = form.cleaned_data['t']
        neg_weight = form.cleaned_data['neg_weight']

        x1_opt,x1_return,x1_std,x2_opt,x2_return,x2_std,myplot = run_algo(stocks, crypto, t, neg_weight)
        
        port1_table = opt_port_table(stocks_list, x1_opt)
        port2_table = opt_port_table(stocks_list + crypto_list, x2_opt)

        form = StonkForm()

    # Perform optimization algo if form is valid
    context = {
        'form': form,
        'eff_front': myplot,
        'port1_table': port1_table,
        'port2_table': port2_table
    }    
    
    return render(request, 'portfolio.html', context)

def about_view(request, *args, **kwargs):
    return render(request, 'about.html', {})


def limitations_view(request, *args, **kwargs):
    return render(request, 'limitations.html', {})