from django.http import HttpResponse
from django.shortcuts import render
from .utils.algo import *
from .forms import StonkForm
import json

# Create your views here.
def home_view(request, *args, **kwargs):
    return render(request, "home.html", {})

def portfolio_view(request, *args, **kwargs):
    form = StonkForm(request.POST or None)
    myplot = None
    port1_table = None
    port2_table = None
    x1_return = None
    x1_std = None
    x2_return = None
    x2_std = None
    stocks = {}
    crypto = {}
    ticker_list = None

    # Preform optimization algo if form is valid and request is POST
    if request.method == 'POST' and form.is_valid():
        stocks, stocks_list = form.cleaned_data['stocks']
        crypto, crypto_list = form.cleaned_data['crypto_stocks']
        t = form.cleaned_data['t']
        neg_weight = form.cleaned_data['neg_weight']

        x1_opt,x1_return,x1_std,x2_opt,x2_return,x2_std,myplot = run_algo(stocks, crypto, t, neg_weight)
        
        port1_table = opt_port_table(stocks_list, x1_opt)
        port2_table = opt_port_table(stocks_list + crypto_list, x2_opt)

        stocks = stocks.to_json(orient='columns')
        crypto = crypto.to_json(orient='columns')

        ticker_list = stocks_list + crypto_list

        # Resets the form
        form = StonkForm()

    # Data needed to be rendered on frontend 
    context = {
        'form': form,
        'stocks': stocks,
        'crypto': crypto,
        'ticker_list': ticker_list,
        'eff_front': myplot,
        'port1_table': port1_table,
        'port2_table': port2_table,
        'x1_return': x1_return[0][0] if x1_return else x1_return,
        'x1_std': x1_std,
        'x2_return': x2_return[0][0] if x2_return else x2_return,
        'x2_std': x2_std
    }    
    
    return render(request, 'portfolio.html', context)

def about_view(request, *args, **kwargs):
    return render(request, 'about.html', {})


def limitations_view(request, *args, **kwargs):
    return render(request, 'limitations.html', {})