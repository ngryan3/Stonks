from pandas.core import base
from requests.api import get
# import matplotlib.pyplot as plt
import base64
from io import BytesIO
from .crypto_api import *
from .stock_api import *
from cvxopt import matrix
from cvxopt.solvers import qp,options
import numpy as np
import pandas as pd
import math
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

def run_algo(stock_data, crpyto_data, t, neg_weight=True):
    #Get stock and crypto data
    # stock_data = get_stock_data(stock_list)[1]
    # crpyto_data = get_crypto_data(crypto_list)[1]

    #Create data frame with both stock and crypto
    data_stock_crypto = stock_data.merge(crpyto_data,on='Date')

    #Calculate % weekly return of both data frames
    #   - one with only stock
    #   - one with stock and crypto
    perc_return_stock = conv_to_perc_return(stock_data)
    perc_return_stock_crypto = conv_to_perc_return(data_stock_crypto) 

    #Calculate covariance matrix
    H_stock = get_cov_matrix(perc_return_stock)
    H_stock_crypto =get_cov_matrix(perc_return_stock_crypto)

    #Calculate mean returns
    rbar_stock = get_mean_return(perc_return_stock)
    rbar_stock_crypto = get_mean_return(perc_return_stock_crypto)

    #Solve for optimal portfolio depending on neg_weight setting
    if neg_weight == True: #Allow negative weights in portfolio
        x1_opt = qp_solver(H_stock,-t*rbar_stock)
        x2_opt = qp_solver(H_stock_crypto,-t*rbar_stock_crypto)
    else: #Restrict to only non-negative weights
        x1_opt = scqp_solve(H_stock,-t*rbar_stock)
        x2_opt = scqp_solve(H_stock_crypto,-t*rbar_stock_crypto)
    
    #Get return and std for optimal portfolios
    x1_return = rbar_stock.T @ x1_opt
    x1_std = math.sqrt(x1_opt.T @ H_stock @ x1_opt)

    x2_return = rbar_stock_crypto.T @ x2_opt
    x2_std = math.sqrt(x2_opt.T @ H_stock_crypto @ x2_opt)
    
    #Plot efficient frontier
    myplot = plot_eff_frontier(H_stock,H_stock_crypto,rbar_stock,rbar_stock_crypto,x1_opt,x2_opt,neg_weight)

    return x1_opt,x1_return,x1_std,x2_opt,x2_return,x2_std,myplot


#Function plots efficient frontier for two optimization problems
def plot_eff_frontier(H1,H2,rbar1,rbar2,x1,x2,neg_weight = True):
    n = 200
    all_t = np.linspace(0,20,num=n)

    #Create empty arrays that will store portfolio return and std dev
    port1_return = np.ones((n,1))
    port1_std = np.ones((n,1))

    port2_return = np.ones((n,1))
    port2_std = np.ones((n,1))
    
    #Set solver function
    solver = qp_solver if neg_weight else scqp_solve

    #Run the solver for all values in all_t
    i=0
    for t in all_t:
       opt_x1 = solver(H1,-t*rbar1)
       opt_x2 = solver(H2,-t*rbar2)
                
       port1_return[i] = rbar1.T @ opt_x1
       port1_std[i] = math.sqrt(opt_x1.T @ H1 @ opt_x1)

       port2_return[i] = rbar2.T @ opt_x2
       port2_std[i] = math.sqrt(opt_x2.T @ H2 @ opt_x2)

       i = i + 1
    
    #Plot efficient frontier using the returns and std dev
    plt.clf()
    plt.plot(port1_std, port1_return)
    plt.plot(port2_std,port2_return)

    plt.xlabel("Standard Deviation (Risk)")
    plt.ylabel("Mean Return")
    plt.title("Efficient Frontier")
    plt.legend(["Stocks Only Portfolios","Stock + Crypto Portfolios"])

    #Plot port x1 onto efficient frontier
    x1_return = rbar1.T @ x1
    x1_std = math.sqrt(x1.T @ H1 @ x1)

    plt.plot(x1_std,x1_return,'ro')

    #Plot port x2 onto efficient frontier
    x2_return = rbar2.T @ x2
    x2_std = math.sqrt(x2.T @ H2 @ x2)

    plt.plot(x2_std,x2_return,'ro')
    
    # Show plot on the webpage
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()

    return graph
    


def scqp_solve(H,g):
    n = len(H)
    x = np.ones((n,1)) / n #Initialze initial weights
    itcount = 0
    
    while True:
        itcount = itcount + 1
                
        S = np.where(x==0)[0]
        len_S = S.size
        A = np.zeros((len_S + 1,n))
        A[0,:] = 1

        if len_S != 0:
            for i in range(0,len_S):
                A[i+1,S[i]] = 1
                    
        b = np.zeros((len_S+1,1))
        b[0] = 1

        A_1 = np.concatenate((H,A.T),axis=1)
        Zeros_m = np.zeros((len_S+1,len_S+1))
        A_2 = np.concatenate((A,Zeros_m),axis=1)

        A_prime = np.concatenate((A_1,A_2),axis=0)
        b_prime = np.concatenate([-g,b])

        u = np.linalg.solve(A_prime,b_prime)

        xtilde = u[0:n]
        w = u[n:]

        np.put(xtilde,S,0)
        
        if np.any((xtilde < 0)):
            #Case 1
            #print("Case 1")
            p = np.subtract(xtilde,x)
            i = np.where(p<0)[0]
            alphastar = np.amin(np.divide(-x[i],p[i]))
            i = np.where(np.divide(-x,p)== alphastar)[0]
            x = x + alphastar*p

            #Set x[S] and x[i] to 0
            x[S] = 0
            x[i] = 0

        else: 
            #Case 2
            #print("Case 2a")
            mu = -w[0]
            z = np.zeros((n,1))
            z[S] = -w[1:(len_S+1)]

            if np.all((z[S] >= 0)):
                #Case 2a
                x = xtilde
                break
            else:
                #Case 2b
                #print("Case 2b")
                minz = np.amin(z)
                jprime = np.asscalar(np.where(z==minz)[0])
                jprime_pos = np.where(S==jprime)

                T = np.where(xtilde >= 0)
                d = np.zeros((n,1))
                d[jprime] = 1
                d[T] = -1/len(T)

                epsilon1 = np.min(np.divide(-xtilde[T],d[T]))
                epsilon2 = -minz/ ( d.T @ H @ d)

                x = xtilde + min(epsilon1,epsilon2)*d
                S_minus_jprime = np.delete(S,jprime_pos)
                x[S_minus_jprime] = 0

         

    return x

def qp_solver(H,g):
    options['show_progress'] = False
    n = len(H)
    H = matrix(H)
    g = matrix(g)

    A = matrix(1.0,(1,n))
    b = matrix(1.0)
    G = matrix(0.0,(n,n))
    h = matrix(0.0,(n,1))

    optx = qp(H,g,G,h,A,b)['x']
    return np.array(optx)

def conv_to_perc_return(df):
    perc_return = df
    perc_return.drop('Date',1,inplace=True)
    perc_return = perc_return.pct_change()*100
    perc_return.drop(0,axis=0,inplace=True)

    return perc_return

def get_cov_matrix(df):
    return df.cov().to_numpy()

def get_mean_return(df):
    g = df.mean(axis=0).to_numpy()
    gprime = g.reshape((-1,1))
    return gprime

def opt_port_table(ticker_list, optimal_arr):
    df = pd.DataFrame(ticker_list, columns=['Tickers'])
    df['Weights (%)'] = optimal_arr    
    df_to_html = df.to_html(classes='table table-sm table-striped table-hover text-center', justify='center', index=False)
    return df_to_html
