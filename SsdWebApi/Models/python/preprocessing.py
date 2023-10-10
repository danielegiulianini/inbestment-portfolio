# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from statistical_tests import kpss


def from_prices_to_returns_npa(prices_npa):
    a = prices_npa / shift_npa(prices_npa, 1)
    a[0] = 1
    return a

def from_prices_to_logreturns_npa(prices_npa):
    return np.log(from_prices_to_returns_npa(prices_npa))

def from_returns_to_prices_npa(returns_npa, initial_price):
    return np.cumprod(returns_npa) * initial_price

def from_logreturns_to_prices_npa(returns_npa, initial_price):
    return from_returns_to_prices(np.exp(returns_npa), initial_price)


#utilities for dataframe
def from_prices_to_returns(prices_df):
    a = prices_df / prices_df.shift(1)
    a.iloc[0] = 1
    return a

def from_prices_to_logreturns(prices_df):
    return np.log(from_prices_to_returns(prices_df))

def from_returns_to_prices(returns_df, initial_price):
    return returns_df.cumprod() * initial_price

def from_logreturns_to_prices(returns_df, initial_price):
    return from_returns_to_prices(np.exp(returns_df), initial_price)



def diff_until_stationary(numpy_array, max_order=1):
    res = numpy_array
    to_ret = res
    old_pvalue = kpss(res)[1]
    for x in range(1, max_order + 1):  
        res = diff(res, x)
        pvalue = kpss(res)[1]
        if pvalue < old_pvalue:
            break
        old_pvalue = pvalue
        to_ret = res
    return to_ret, pvalue > 0.05

def undiff(npa, original_npa, order, debug = False):
    ret = npa
    for i in range(order, 0, -1):
        ret[i-1] = diff(original_npa, i-1)[i-1]
        ret = ret.cumsum()
    return ret

def diff(numpy_array, order=1):
    res = numpy_array
    while (order > 0):
        res = pd.Series(res).diff()
        order -=1
    return nan_to_zero_and_inf_to_edges(res)

def nan_to_zero_and_inf_to_edges(numpy_array):
    return np.nan_to_num(numpy_array)

#function anologue to dataframe.shift, but for numpy arrays    
def shift_npa(npa, pos = 1):
    npa = np.roll(npa, pos)
    if pos > 0:
        for i in range(pos):
            if i < len(npa):
                npa[i] = float("nan")
    else:
        for i in range(pos, 0):
            if -i <= len(npa):
                npa[i] = float("nan")
    return npa

