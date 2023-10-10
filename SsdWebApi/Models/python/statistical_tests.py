# -*- coding: utf-8 -*-


from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss
import statsmodels.stats.diagnostic as diag

#removing harmless warning
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter('ignore', InterpolationWarning)



#STATIONARITY TESTS
def kpss_test(series, **kw):
    #null hypotheses: stationary data series
    statistic, p_value, n_lags, critical_values = kpss(series, **kw)
    print(f'KPSS test: series {"not " if p_value < 0.05 else ""} stationary')

def adfuller_test(numpy_array):
    #null hypotheses: unit root present
    result = adfuller(numpy_array)
    pvalue = result[1]
    print('adfuller test: series ', end='')
    if pvalue > 0.05 :
        print('not ', end='')
    print('stationary.')
    
    
    
#HETEROSKEDASTICITY TESTS
def lunjbox_test(ndarray):
    #null hypotheses: no autocorrelation (if < threshold => autocorr => heterosk)
    print("ljung-box's test: serial auto correlation ", end='')
    nlags = min(10, len(ndarray) // 5)
    test_output = diag.acorr_ljungbox(ndarray, lags=nlags, return_df=True, model_df = 0)
    pvalue, bppvalue = test_output[1], test_output[3]
    not_correlated = pvalue > 0.05 and bppvalue > 0.05
    if not_correlated:
        print("not ", end = '')
    print("present.")


#to be performed on ARIMA standardized residuals
def het_arch_test(ndarray, ddof):
    #null hypotheses: homoskedastic
    print("engles's test: eteroskedasticity ", end = '')   #if p-v < 0.05 => no homo => heterosk
    nlags = min(10, len(ndarray) // 5)
    res = diag.het_arch(ndarray, nlags=nlags)
    lm_p_value = res[1]
    f_p_value = res[3]
    homoskedastic = lm_p_value > 0.05 and f_p_value > 0.05
    if homoskedastic:
        print("not ", end = '')
    print("present.")
    return lm_p_value < 0.05 or f_p_value < 0.05
