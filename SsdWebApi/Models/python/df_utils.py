# -*- coding: utf-8 -*-

import pandas as pd


def append_to_df(df, index, to_be_appended):
    series = pd.Series(to_be_appended)      #return df.append(pd.Series(to_be_appended))
    series.name = index
    return df.append(series)

def change_index(df, index):
    return pd.Series(df, index = index)

def split_at(npa, cutpoint):
    return npa[:-cutpoint], npa[-cutpoint:]