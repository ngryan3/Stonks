from django.forms import widgets
import yfinance as yf
from .utils.crypto_api import *
from .utils.stock_api import *
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.timeseries import TimeSeries

from django import forms


class StonkForm(forms.Form):
    stocks = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Stocks Here'}))
    crypto_stocks = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Crypto Stocks Here'}))
    t = forms.FloatField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter t Value Here'}))
    neg_weight = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # Requirements:
    # 1) At most 20 stocks in total
    # 2) All stocks must have been around for at leasy 2 years

    def clean_crypto_stocks(self):
        """
        Checks if all the crypto stocks satisfy Requirements 
        """
        crypto_stocks = self.cleaned_data.get('crypto_stocks')
        crypto_list = [crypto.strip() for crypto in crypto_stocks.split(',')]

        cc = CryptoCurrencies(key='BNHVRTHJ2BUK74AB', output_format='pandas')

        # Check if there is at most 5 cryto stocks
        if len(crypto_list) > 5:
            raise forms.ValidationError("Maximum number of crypto stocks exceeded")

        # Check for uniqueness
        if len(crypto_list) != len(set(crypto_list)):
            raise forms.ValidationError("All crypto stocks must be unique")

        # Check if crypto stocks are valid in the alpha_vantage lib
        try:
            crypto_df = get_crypto_data(crypto_list)
            if crypto_df[0] == -1:
                raise forms.ValidationError("{} is not a valid crypto stock".format(crypto_df[1]))
            elif crypto_df[0] == -2:
                raise forms.ValidationError("{} has not been around for at least 2 years".format(crypto_df[1]))
        # Happens when the user tries to run the algo again even though 1 minute has not passed
        except:
            raise forms.ValidationError("Please wait 1 minute before running the algorithm again")

        return crypto_df[1], crypto_list
    
    
    def clean_stocks(self):
        """
        Checks if all the stocks satisfy Requirements 
        """
        stocks = self.cleaned_data.get('stocks')
        stocks_list = [stock.strip() for stock in stocks.split(',')]

        ts = TimeSeries('BNHVRTHJ2BUK74AB', output_format='pandas')

        # Check if there is at most 15 stocks
        if len(stocks_list) > 15:
            raise forms.ValidationError("Maximum number of stocks exceeded")

        # Check for uniqueness
        if len(stocks_list) != len(set(stocks_list)):
            raise forms.ValidationError("All stocks must be unique")

        # Check if stocks are valid in the yfinance lib
        stocks_df = get_stock_data(stocks_list)
        if stocks_df[0] == -1:
            raise forms.ValidationError("{} is not a valid stock".format(stocks_df[1]))
        elif stocks_df[0] == -2:
            raise forms.ValidationError("{} has not been around for at least 2 years".format(stocks_df[1]))

        return stocks_df[1], stocks_list