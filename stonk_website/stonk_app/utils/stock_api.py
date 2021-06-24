#pip install yfinance
import yfinance as yf
import pandas as pd
import datetime as dt

def get_ticker():
    return input()

def get_stock_ticker_data(ticker):
    the_ticker = yf.Ticker(ticker)
    hist = the_ticker.history(period="2y", interval='1wk')
    if hist.empty:
        return -1
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

def two_year_restriction(date_list):
    date = dt.date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
    if (dt.date.today() - date).days / 365 < 2:
        return False
    return True

def get_stock_start_date(df):
    #gets the first monday
    bool = True
    i = 0
    initial = date_string(df['Date'][i]).split('-')

    if two_year_restriction(initial) is False:
        bool = False
        #print("2 years of data not available for this ticker")
        return -2
        
    while bool:
        start_date = date_string(df['Date'][i])
        date_list = start_date.split('-')
        if dt.date(int(date_list[0]), int(date_list[1]), int(date_list[2])).weekday() == 0:
            bool = False
            return start_date
        else:
            i += 1

def get_stock_weekly_data(df, start_date, ticker):
    df_week = pd.DataFrame()
    test_list = []
    date_list = []
    next_date = start_date
    test_list.append(next_date)
    while df['Date'][len(df)-1] >= date_split(next_date):
        next_date = date_split(next_date) + dt.timedelta(days = 7)
        next_date = date_string(next_date)
        test_list.append(next_date)
    test_list = sorted(set(test_list), key=test_list.index)
    for i in range(len(test_list)):
        df_week = df_week.append(df.loc[df['Date'] == test_list[i]])
    price = ticker+' Closing price'
    time = ticker+' Date'
    df_week = df_week.rename(columns = {'Close': price, 'Date': time})
    for i in range(len(df_week[time])):
       date_list.append(date_string(pd.to_datetime(df_week[time].values[i])))
    df_week = df_week.reset_index(drop = True)
    df_week.dropna(subset=[ticker+" Closing price"], inplace=True) 
    df_week[time].update(date_list)
    df_week = df_week.reset_index(drop = True)
    if len(df_week) != 104:
        df_week = df_week.iloc[len(df_week)-104:]
    return df_week

def get_stock_inputs():
    number = input() # max idk
    number = int(number)
    ticker_list = []
    for i in range(1, number+1):
        ticker_list.append(input())
        i += 1
    return ticker_list

def get_stock_data(ticker_list):
    if ticker_list == []:
        return 
    df_final = pd.DataFrame()
    for index, ticker in enumerate(ticker_list):
        data = get_stock_ticker_data(ticker)
        if type(data) == int:
            return (-1, ticker)
        date1 = get_stock_start_date(data)
        if date1 == -2:
            return (-2, ticker)

        df = get_stock_weekly_data(data, date1, ticker)
          
        df_final = pd.concat([df_final, df], axis = 1)
        if index != 0:
            #print(df_final[ticker_list[i]+' Date'].tolist() == df_final[ticker_list[0]+' Date'].tolist())
            if df_final[ticker +' Date'].tolist() == df_final[ticker_list[0]+' Date'].tolist():
                df_final = df_final.drop(ticker+ ' Date', axis = 1)
    cols = df_final.columns.tolist()
    index = cols[1]
    cols.remove(ticker_list[0]+' Date')
    cols.append(index)
    df_final = df_final[cols]
    df_final = df_final.rename(columns={ticker_list[0]+' Date': 'Date'})
    df_final = df_final.reset_index(drop = True)
    return (0, df_final)


def s_turn_to_csv(df):
    df.to_csv('stock.csv', index = False)
