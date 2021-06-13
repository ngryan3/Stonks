#pip install yfinance
import yfinance as yf
import pandas as pd

def get_ticker():
    return input()

def get_ticker_data(ticker):
    the_ticker = yf.Ticker(ticker)
    hist = the_ticker.history(period="max")
    hist = hist.reset_index()
    #type(hist) #pandas dataframe

    df_Stock = pd.DataFrame()
    df_Stock = df_Stock.assign(Close = hist['Close'].values)
    df_Stock = df_Stock.assign(Date = hist['Date'].values)

    return df_Stock

def date_split(date):
    #input is in the form of '2020-04-27'
    date = date.split('-')
    next_date = dt.date(int(date[0]), int(date[1]), int(date[2]))
    return next_date

def date_string(date):
    #input is a datetime object
    return date.strftime("%Y-%m-%d")

def get_start_date(df):
    #gets the first monday
    bool = True
    i = 0
    while bool:
        start_date = date_string(df['Date'][i])
        date_list = start_date.split('-')
        if dt.date(int(date_list[0]), int(date_list[1]), int(date_list[2])).weekday() == 0:
            bool = False
            print(start_date)
            return start_date
        else:
            i += 1

def get_weekly_data(df, start_date):
    df_week = pd.DataFrame()
    test_list = []
    next_date = start_date
    test_list.append(next_date)
    while df['Date'][len(df)-1] >= date_split(next_date):
        next_date = date_split(next_date) + dt.timedelta(days = 7)
        next_date = date_string(next_date)
        test_list.append(next_date)

    test_list.pop(-1)
    for i in range(len(test_list)):
        df_week = df_week.append(df.loc[df['Date'] == test_list[i]])
    return df_week


def turn_to_csv(ticker, df):
    df.to_csv(ticker+'.csv')


