# Helper Functions
import yfinance as yf
import pandas as pd
from plotly.offline import plot
import plotly.graph_objects as go

def get_stocks_data(stocks):
    df_final = pd.DataFrame()
    for stock in stocks:
        ticker = yf.Ticker(stock)

        hist = ticker.history(period='2y', interval='1wk')
        
        # Remove rows where the dividends and stock splits are not 0
        try:
            hist = hist[(hist['Dividends'] == 0) & (hist['Stock Splits'] == 0)]
        except:
            return (-1, stock)

        # Check if stock is at least 2 years old
        if len(hist) < 104:
            return (-2, stock)

        df_final['{} Close'.format(stock)] = hist['Close']

    return (0, df_final)
    


def get_crypto_data(crypto):
    pass


def main_algo(stock_data, crypto_data, t):
    pass


def demo_plot():
    # Generating some data for plots.
    x = [i for i in range(-10, 11)]
    y1 = [3*i for i in x]
    y2 = [i**2 for i in x]
    y3 = [10*abs(i) for i in x]

    # List of graph objects for figure.
    # Each object will contain on series of data.
    graphs = []

    # Adding linear plot of y1 vs. x.
    graphs.append(
        go.Scatter(x=x, y=y1, mode='lines', name='Line y1')
    )

    # Adding scatter plot of y2 vs. x. 
    # Size of markers defined by y2 value.
    graphs.append(
        go.Scatter(x=x, y=y2, mode='markers', opacity=0.8, 
                   marker_size=y2, name='Scatter y2')
    )

    # Adding bar plot of y3 vs x.
    graphs.append(
        go.Bar(x=x, y=y3, name='Bar y3')
    )

    # Setting layout of the figure.
    layout = {
        'title': 'Title of the figure',
        'xaxis_title': 'X',
        'yaxis_title': 'Y',
        'height': 420,
        'width': 560,
    }

    # Getting HTML needed to render the plot.
    plot_div = plot({'data': graphs, 'layout': layout}, 
                    output_type='div')
    
    return plot_div

if __name__ == "__main__":
    test = ['TD', 'RY']
    print(get_stocks_data(test))