# -*- coding: utf-8 -*-


import matplotlib.pyplot as plt
import pmdarima as pm
from arch import arch_model

from whs import read_indexes
from statistical_tests import adfuller_test, kpss_test, het_arch_test
from preprocessing import from_prices_to_logreturns_npa


def plot(data, title):
    plt.figure()
    plt.title(title)
    plt.plot(data)


def plots(suptitle, fs_title, fs_data, s_title, s_data, t_title, t_data, ft_title,ft_data):
    fig, axs = plt.subplots(2, 2, figsize=(9,6))
    fig.suptitle(suptitle)
    axs[0, 0].plot(fs_data)
    axs[0, 0].set_title(fs_title)
    axs[0, 1].plot(s_data)
    axs[0, 1].set_title(s_title)
    axs[1, 0].plot(t_data)
    axs[1, 0].set_title(t_title)
    axs[1, 1].plot(ft_data)
    axs[1, 1].set_title(ft_title)
    fig.tight_layout()


if __name__ == '__main__':
    
    time_series_filenames = ["S&P_500_INDEX.csv", "U.S._Treasury.csv","MSCI_EM.csv", "MSCI_EURO.csv", "GOLD_SPOT_$_OZ.csv", "FTSE_MIB_INDEX.csv", "All_Bonds_TR.csv"]
    
    #data reading
    data = read_indexes(time_series_filenames)
    
    #preprocessing
    preproc = {}
    for asset in data.keys():
        preproc[asset] = from_prices_to_logreturns_npa(data[asset])
    
    resid, std_resid = {}, {}
    
    #properties tests
    for asset in data.keys():
        
        print('---asset ' + asset + ' ACTUAL:---')

        #stationarity test
        adfuller_test(data[asset])
        kpss_test(data[asset], nlags = "auto")
        
        print('---asset ' + asset + ' PREPROC:---')

        #stationarity test
        adfuller_test(preproc[asset])
        kpss_test(preproc[asset], nlags="auto")

        
        print('---asset ' + asset + ' ARIMA-RESIDUALS:---')
        
        arima_model = pm.auto_arima(preproc[asset], 
                          start_p=1, max_p=3, 
                          start_q=1, max_q=3, 
                          test='adf', 
                          d=None,     #order of first-differencing
                          seasonal=False,
                          trace=False,
                          error_action='ignore',
                          suppress_warnings=True,
                          stepwise=True)
        
        arima_model.fit(preproc[asset])
        
        resid[asset] = arima_model.resid()
        
        #eteroskedasticity test
        het_arch_test(resid[asset], ddof = sum(list(arima_model.order)))
        
        print('---asset ' + asset + ' GARCH-STANDARDIZED RESIDUALS:---')
        
        garch_model  = arch_model(resid[asset],  mean='Zero', vol = "Garch",
                                  p = 1, o = 0, q = 1,
                                  dist="Normal", rescale = True)
        
        fitted = garch_model.fit(disp='off')
        
        
        std_resid[asset] = resid[asset] / fitted.conditional_volatility # or (resid[asset] + fitted.resid) / if using mean in arch model
        
        het_arch_test(std_resid[asset], ddof = sum(list(arima_model.order)))

        plots(asset, 
              'actual', data[asset], 
              'preproc', preproc[asset], 
              'conditional volatility', fitted.conditional_volatility,
              'std residuals', std_resid[asset])
