# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os, sys, io, base64
import numpy as np
import pandas as pd
import pmdarima as pm
from sklearn import metrics
import json

#custom utilities
from preprocessing import from_prices_to_logreturns, from_logreturns_to_prices
from df_utils import change_index, split_at
from arima_garch_utils import arima_rolling_forecast



def get_accuracy_metrics(actual, y_pred):
    return {'mae' : metrics.mean_absolute_error(actual, y_pred), 
            'mape' : metrics.mean_absolute_percentage_error(actual, y_pred),
            'mse' : metrics.mean_squared_error(actual, y_pred),
            'rmse' : np.sqrt(metrics.mean_squared_error(actual, y_pred))}

class Forecast:
    def __init__(self, text, img, validation, model_info):
        self.text = text
        self.img = img
        self.validation = validation
        self.model_info = model_info
        
        
def as_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    return base64.b64encode(buf.getbuffer())


def get_image_plot(past_data_df, future_data_df, title=''):
    fig, ax = plt.subplots(figsize = (8, 4))  #figure containing single axes
    ax.set_title(title)
    ax.plot(past_data_df, label = 'past')
    ax.plot(future_data_df, label = 'forecasts')
    plt.xlabel("time") ; plt.ylabel("prices")
    ax.plot()
    plt.legend(loc='upper left', fontsize=13)#;ax.show()
    return plt.gcf()



def forecast_index(index_csv_filename, forecast_horizon):
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    
    df = pd.read_csv("../assets/" + index_csv_filename, sep=';', decimal=',')
    
    test_cardinality = 261+180  #test: 2 years = 261(2019) + 180 (2020)

    indexId = index_csv_filename.replace('.csv', '')

    #PREPROCESSING
    #date-adjusting
    df['Dates'] = df['Dates'].apply(pd.to_datetime)
    df = df.set_index('Dates')
    df = df.asfreq('B')
    
    #translating 1. from prices to returns and 2. from returns to log returns
    preproc = from_prices_to_logreturns(df)
    
    #TRAIN-TEST SPLIT
    train, test = split_at(npa = df, cutpoint = test_cardinality)
    preproc_train, preproc_test = split_at(npa = preproc, cutpoint = test_cardinality)

    #MODEL DEFINITION
    model = pm.auto_arima(preproc_train, 
                          start_p = 1, max_p = 3,
                          d = None,     #order of first-differencing
                          start_q = 1, max_q = 3,
                          test = 'adf',
                          seasonal = False,
                          trace = False,
                          error_action = 'ignore',
                          suppress_warnings = True,
                          stepwise = True)
    
    
    #MODEL FITTING on train + FORECAST on test
    preproc_fore_test = arima_rolling_forecast(model, preproc_train, test_cardinality, len(preproc_train)//10)   #preproc_fore_test = fitted.predict(n_periods = test_cardinality)

    #POSTPROCESSING
    postproc_fore_test = from_logreturns_to_prices(preproc_fore_test, train.values[-1][0])

    #COMPUTE ACCURACY METRICS
    accuracy_m = get_accuracy_metrics(test, postproc_fore_test)

    #MODEL FITTING on train+test + FORECAST
    preproc_fore = arima_rolling_forecast(model, preproc, forecast_horizon, len(preproc)//10)   #fitted.predict(n_periods = forecast_horizon)

    #POSTPROCESSING
    postproc_fore = from_logreturns_to_prices(preproc_fore, test.values[-1][0])
    
    #DISPLAY INFO
    forecasts_index = pd.date_range(df.index[-1], periods = forecast_horizon + 1, freq='B', closed = "right")
    postproc_fore_as_df = change_index(postproc_fore, index = forecasts_index)
    
    img = get_image_plot(df, postproc_fore_as_df, indexId)


    forecast_obj = Forecast(
        model_info = {"model" : "arima", "order" : model.order },
        text = change_index(postproc_fore, index = forecasts_index.strftime('%Y-%m-%d')).to_dict(),
        img = as_base64(img).decode('utf8'),
        validation = accuracy_m)
    
    return forecast_obj




if __name__ == '__main__':
    
    time_series_file = sys.argv[1]
    
    forecast_horizon = 261      #forecast: 1 year = 261(2021)
    
    forecast_obj = forecast_index(time_series_file, forecast_horizon)
    
    print(json.dumps(forecast_obj.__dict__))
    