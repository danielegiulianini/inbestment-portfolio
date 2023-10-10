# -*- coding: utf-8 -*-

import os
import numpy as np
import math as m
import pandas as pd
import random as rd
import pmdarima as pm

#custom utilities
from preprocessing import from_prices_to_logreturns_npa, from_logreturns_to_prices
from df_utils import split_at
from arima_garch_utils import arima_rolling_forecast_in_sample, garch_rolling_forecast_in_sample



def read_indexes(time_series_filenames, display = False):
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    
    if display:
        print('reading indexes...')

    data = {}
    for time_series_file in time_series_filenames:
        df = pd.read_csv("../assets/" + time_series_file, sep=';', decimal=',')
        asset = time_series_file[:-len('.csv')]
        data[asset] = df[asset].values
        
    if display:
        print('...done')

    return data


def prepare_for_whs(data, sample_size):
    
    #---preprocessing---
    preproc = {}
    for asset in data.keys():
        preproc[asset] = from_prices_to_logreturns_npa(data[asset])
        
    
    train, sample, iid_sample, tomorrow_volatility = {}, {}, {}, {}
    for asset in data.keys():
        
        train[asset], sample[asset] = split_at(preproc[asset], sample_size)

        #mean forecast
        arima_model = pm.auto_arima(train[asset], 
                          start_p=1, max_p=3, 
                          start_q=1, max_q=3, 
                          test='adf', 
                          d=None,     #order of first-differencing
                          seasonal=False,
                          trace=False,
                          error_action='ignore',
                          suppress_warnings=True,
                          stepwise=True)
        
        arima_cond_mean = arima_rolling_forecast_in_sample(arima_model, train[asset], sample_size + 1, len(train[asset]))
        
        #variance forecast
        cond_mean, cond_var = garch_rolling_forecast_in_sample(train[asset], sample_size + 1, len(train[asset]))

        cond_mean = arima_cond_mean + cond_mean
        
        volatilities = np.sqrt(cond_var)
        
        tomorrow_volatility[asset] = volatilities[-1]
        
        volatilities, cond_mean = volatilities[:-1], cond_mean[:-1]
        
        #returns stardardization (de-mean too) for removing serial correlations
        iid_sample[asset] = np.divide(sample[asset] - cond_mean, volatilities)
        
    
    return iid_sample, tomorrow_volatility


def volatility_weighted_historical_simulation(
        data,                       #dictionary with past time series index data (prices)
        iid_sample,                 #sample of contiguous standardized returns (logreturns)
        tomorrow_volatility,        #latest estimate of volatility
        forecast_horizon,
        weight_array,               #portfolio percentual composition between assets
        drawings_count = 1000):     #count of simulated observations to base VaR computation on

    sample_size = len(next(iter(iid_sample.values())))
    
    #compute initial portfolio price value
    initial_portfolio_value = np.dot([data[asset][-1] for asset in data.keys()], weight_array)
    
    simulated_losses_or_gains = []
    
    for dc in range(drawings_count + 1):
        
        #random draw (with replacement) a drawing index from the ones of iid sample
        drawing_index = rd.randint(0, sample_size - 1)

        prices_row = {}

        for asset in data.keys():
            
            #select random draw (same date for every asset)
            drawing = iid_sample[asset][drawing_index]

            #multiply drawing by latest estimate of volatility to reflect most recent asset conditions
            rescaled_drawing = drawing * tomorrow_volatility[asset]  #print('rescaled drawing for asset ' + str(asset)+':'+str(rescaled_drawing))
            
            #logreturns-to-prices translation
            rescaled_price = from_logreturns_to_prices([rescaled_drawing], data[asset][-1])[0]
            
            #get last forecast corresponding to desired forecast horizon
            prices_row[asset] = rescaled_price
            
        #by-weight-fusion of the row => simulated price observation
        simulated_portfolio_price = np.dot([prices_row[asset] for asset in prices_row.keys()], weight_array)
        
        #convert simulated price to profit/loss value
        simulated_portfolio_loss_or_gain = simulated_portfolio_price - initial_portfolio_value
        
        #asimulated P/L obs accumulation
        simulated_losses_or_gains.append(simulated_portfolio_loss_or_gain)
    
    var = - np.percentile(simulated_losses_or_gains, [1,5])       
    
    return {"5%":var[0] * m.sqrt(forecast_horizon), 
            "1%":var[1] * m.sqrt(forecast_horizon)}



def volatility_weighted_historical_simulation_w_std(
        data,                       #a dictionary with indexes time series
        forecast_horizon,
        weight_array,               #the portfolio percentage composition
        sample_size = 250,          #size of iid sample where by draw observations 
        drawings_count = 1000):     #simulated observations

    iid_sample, tomorrow_volatility = prepare_for_whs(data, sample_size)
    
    return volatility_weighted_historical_simulation(data,
                                                     iid_sample = iid_sample,
                                                     tomorrow_volatility = tomorrow_volatility,
                                                     forecast_horizon = forecast_horizon,
                                                     weight_array = weight_array,
                                                     drawings_count = drawings_count)













#example of use
if __name__ == '__main__':

    forecast_horizon = 261    #forecast: 1 years = 261(2021)
    
    time_series_filenames = ["S&P_500_INDEX.csv", "U.S._Treasury.csv", "MSCI_EM.csv", "MSCI_EURO.csv", "GOLD_SPOT_$_OZ.csv", "FTSE_MIB_INDEX.csv", "All_Bonds_TR.csv"] #or: time_series_file = sys.argv[1]
    
    #---data reading---
    data = read_indexes(time_series_filenames)
    
    #---FILTERED HISTORICAL SIMULATION---
    weight_array = [.1, .1, .1, .1, .1, .1, .1]
    sample_size = 250       #size of iid sample from which draw observations 
    drawings_count = 2000   #simulated observations
    
    value_at_risk = volatility_weighted_historical_simulation_w_std(
                                    data = data,
                                    forecast_horizon = forecast_horizon,
                                    weight_array = weight_array,
                                    sample_size = sample_size,
                                    drawings_count = drawings_count)
    

    print("5% VaR: " + str(value_at_risk["5%"]))
    print("1% VaR: " + str(value_at_risk["1%"]))
    
