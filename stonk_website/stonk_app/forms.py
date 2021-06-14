import yfinance as yf

from django import forms


class StonkForm(forms.Form):
    stocks = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Stocks Here'}))
    crypto_stocks = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Crypto Stocks Here'}))
    t = forms.FloatField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter t Value Here'}))

    # Requirements:
    # 1) At most 20 stocks in total
    # 2) All stocks must have been around for at leasy 2 years

    def clean_num_stocks(self):
        stocks = self.cleaned_data.get('stocks')
        crypto_stocks = self.cleaned_data.get('crypto_stocks')
        
        stocks_list = [stock.strip() for stock in stocks.split(',')]
        crypto_stocks_list = [crypto_stocks.strip() for crypto in crypto_stocks.split(',')]

        if len(stocks_list + crypto_stocks_list) > 20:
            raise forms.ValidationError("Maximum number of stocks exceeded")


    # Need an api to check if the selected stocks are crypto and satisfy the previous requirements
    def clean_crypto_stocks(self):
        pass
    
    
    def clean_stocks(self):
        """
        Checks if all the stocks satisfy Requirement 2
        """
        stocks = self.cleaned_data.get('stocks')

        stocks_list = [stock.strip() for stock in stocks.split(',')]
        
        for stock in stocks_list:
            ticker = yf.Ticker(stock)
            ticker_data = ticker.history(period='2y', interval='1wk')
            
            if len(ticker_data) < 114:
                raise forms.ValidationError("{} is not a valid stock".format(stock))
        return stocks_list
    
    # Need to check for maximum of 20 stonks selected 