# -*- coding: utf-8 -*-

import numpy as np
from arch import arch_model



def garch_rolling_forecast_in_sample(train, horizon, window_size):
    """
    Outputs garch(1, 1) mean and variance forecasts by accumulating the
    1-step forecasts obtained by fitting iteratively the model on a sliding 
    window of fixed size (given by window_size) of the train data provided.
    Wrt garch_rolling_forecast, the new input window for fitting is 
    iteratively appended values coming not from the forecasted values but 
    from the provided.
    """
    
    if window_size > len(train - horizon):
        raise ValueError('window_size must be smaller or equal to train length')
        
    mean_forecasts, var_forecasts = [], []
    
    for t in range(horizon):
        
        #w/o window: model  = arch_model(train[t : len(train) - horizon + t],  mean='Constant', vol = "Garch", p = 1, o = 0, q = 1, dist="skewt", rescale = True)    #dist='Normal'
        
        model  = arch_model(train[ len(train-horizon) - window_size + t: len(train) - horizon  + t],  mean='Zero', vol = "Garch", p = 1, o = 0, q = 1, dist="skewt", rescale = True)    #dist='Normal'
        fitted = model.fit(disp='off')
        forecast = fitted.forecast(horizon = 1, reindex = False)
        
        mean_forecast = forecast.mean.iloc[-1].values[0] / model.scale
        var_forecast = forecast.variance.iloc[-1].values[0] / np.power(model.scale, 2)
        
        mean_forecasts.append(mean_forecast)
        var_forecasts.append(var_forecast)
        
    return np.asarray(mean_forecasts), np.asarray(var_forecasts)



def arima_rolling_forecast_in_sample(arima_model, train, horizon, window_size):
    """
    Outputs the given-arima-model' mean forecasts for the horizon by 
    accumulating the 1-step forecasts obtained by fitting iteratively 
    the model on a sliding window of fixed size (given by window_size) 
    of the train data provided.
    Wrt arima_rolling_forecast, the new input window for fitting is 
    iteratively appended values coming not from the forecasted values but 
    from the provided.
    """
    
    if window_size > len(train - horizon):
        raise ValueError('window_size must be smaller or equal to train length')
    
    forecasts = []
        
    for t in range(horizon):
        fitted = arima_model.fit(train[ len(train-horizon) - window_size + t: len(train) - horizon  + t])
        forecast = fitted.predict(n_periods = 1)[0]

        forecasts.append(forecast)
        
    return np.asarray(forecasts)


def garch_rolling_forecast(train, horizon, window_size):
    """
    Performs a rolling fixed-window forecast of mean and variance, that is: 
    a multi-horizon forecast obtained by accumulating iteratively the 1-step 
    horizon forecasts obtained by refitting a GARCH(1, 1) model on a fixed 
    window (of window_size) made of the past values + the data forecasted by 
    the model at the previous iterations.
    """
    
    if window_size > len(train):
        raise ValueError('window_size must be smaller or equal to train length')
    
    mean_forecasts, var_forecasts = [], []
    history = train
    
    for t in range(horizon):
        model  = arch_model(history[len(train) - window_size + t : len(train) + t ],  mean='Constant', vol = "Garch", p = 1, o = 0, q = 1, dist="skewt", rescale = True)    #dist='Normal'
        fitted = model.fit(disp='off')
        forecast = fitted.forecast(horizon = 1, reindex = False)
        
        mean_forecast = forecast.mean.iloc[-1].values[0] / model.scale
        var_forecast = forecast.variance.iloc[-1].values[0] / np.power(model.scale, 2)
        
        mean_forecasts.append(mean_forecast)
        var_forecasts.append(var_forecast)
        
        history = np.append(history, mean_forecast)
        
    return np.asarray(mean_forecasts), np.asarray(var_forecasts)


def arima_rolling_forecast(arima_model, train, horizon, window_size):
    """
    Performs a rolling fixed-window forecast of horizon future mean values, 
    that is: 
    a multi-horizon forecast obtained by accumulating iteratively the 1-step 
    horizon forecasts obtained by refitting the given model on a fixed window 
    (of window_size) made of the past values + the data forecasted by the 
    model at the previous iterations.
    """
    
    if window_size > len(train):
        raise ValueError('window_size must be smaller or equal to train length')
    
    forecasts = []
    history = train
        
    for t in range(horizon):
        fitted = arima_model.fit(history[len(train) - window_size + t : len(train) + t ])
        forecast = fitted.predict(n_periods = 1)[0]

        forecasts.append(forecast)
        history = np.append(history, forecast)
        
    return np.asarray(forecasts)