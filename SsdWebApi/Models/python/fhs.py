# -*- coding: utf-8 -*-



import numpy as np
from arch import arch_model
import random as rd

from preprocessing import from_logreturns_to_prices, from_prices_to_logreturns_npa
from whs import prepare_for_whs, read_indexes


def filtered_historical_simulation(
        data,                       #dictionary with past time series index data (prices)
        iid_sample,                 #sample of contiguous standardized returns (logreturns)
        forecast_horizon,
        weight_array,               #portfolio percentual composition between assets
        drawings_count = 1000):     #count of simulated observations to base VaR computation on
    

    sample_size = len(next(iter(iid_sample.values())))
    
    preproc = {}
    for asset in data.keys():
        preproc[asset] = from_prices_to_logreturns_npa(data[asset])
    
    #compute initial portfolio price value
    initial_portfolio_value = np.dot([data[asset][-1] for asset in data.keys()], weight_array)

    simulated_losses_or_gains = []
    
    for dc in range(drawings_count + 1):
        
        #this-iter's training data copy for GARCH (to be growed)
        thisobs_train = preproc.copy()

        for _ in range(forecast_horizon + 1):
            
            #random draw (with replacement) a drawing index from the ones of iid sample
            drawing_index = rd.randint(0, sample_size - 1)
            
            for asset in thisobs_train.keys():
                
                #1-step forecast
                am = arch_model(thisobs_train[asset], vol = "Garch", p = 1, o = 0, q = 1, dist="skewt", rescale = True)
                
                res = am.fit(disp = "off", show_warning = False, options = {'maxiter': 500})
                
                forecasts = res.forecast(horizon = 1, reindex = False)
                
                tomorrow_cond_var = forecasts.variance.iloc[-1][0] / np.power(am.scale, 2)
                
                #get forecasted volatility as root square of forecasted variance
                tomorrow_vol = np.sqrt(tomorrow_cond_var) 
                
                #select random draw (same date for every asset)
                drawing = iid_sample[asset][drawing_index]

                #rescale drawing according to most recent volatility
                rescaled_drawing = drawing * tomorrow_vol  
                
                thisobs_train[asset] = np.append(thisobs_train[asset], rescaled_drawing)
        
        #conversion from logreturns to prices
        prices_row = {}
        for asset in thisobs_train.keys():
            
            #logreturns to prices translation
            thisobs_train_prices = from_logreturns_to_prices(thisobs_train[asset][-forecast_horizon:], 
                                                             data[asset][0])
            
            #get last forecast corresponding to desired forecast horizon
            prices_row[asset] = thisobs_train_prices[-1]
            

        #by-weight-fusion of the row => simulated price obs
        observation = np.dot([prices_row[asset] for asset in prices_row.keys()], weight_array)
        
        #convert simulated price to profit/loss value
        simulated_loss_or_gain = observation - initial_portfolio_value
        
        #simulated-profit/loss-observation accumulation
        simulated_losses_or_gains.append(simulated_loss_or_gain)
    
    #compute 1% and 5% var as a percentile of simulated observations
    var = - np.percentile(simulated_losses_or_gains, [1, 5], interpolation='linear')       
    
    return {"5%":var[1], "1%":var[0]}




def filtered_historical_simulation_w_std(
    data,                       #a dictionary with indexes time series
    forecast_horizon,
    weight_array,
    sample_size = 250,          #size of iid sample from which observations are drawn
    drawings_count = 1000):     #simulated observations


    iid_sample, tomorrow_volatility = prepare_for_whs(data, sample_size)
    return filtered_historical_simulation(data,
                                          iid_sample = iid_sample,
                                          forecast_horizon = forecast_horizon,
                                          weight_array = weight_array,
                                          drawings_count = drawings_count)









if __name__ == '__main__':

    forecast_horizon = 10
    
    time_series_filenames = ["S&P_500_INDEX.csv", "U.S._Treasury.csv", "MSCI_EM.csv", "MSCI_EURO.csv", "GOLD_SPOT_$_OZ.csv", "FTSE_MIB_INDEX.csv", "All_Bonds_TR.csv"] #or: time_series_file = sys.argv[1]
    
    #---data reading---
    data = read_indexes(time_series_filenames)

    #---FILTERED HISTORICAL SIMULATION---
    weight_array = [.1, .1, .1, .1, .1, .1, .1]
    sample_size = 250           #size of iid sample whereby observations are drawn
    drawings_count = 1000       #simulated observations
    
    value_at_risk = filtered_historical_simulation_w_std(
                                    data = data,
                                    forecast_horizon = forecast_horizon,
                                    weight_array = weight_array,
                                    sample_size = sample_size,
                                    drawings_count = drawings_count)
    
    print("5% VaR: " + str(value_at_risk["5%"]))
    print("1% VaR: " + str(value_at_risk["1%"]))






