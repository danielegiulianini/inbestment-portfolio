# -*- coding: utf-8 -*-

import os
import pandas as pd
from time_utils import get_next_date 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.compose import TransformedTargetRegressor
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import AdaBoostRegressor, ExtraTreesRegressor, RandomForestRegressor
from sklearn.model_selection import cross_val_score, TimeSeriesSplit, GridSearchCV


from forecast_arima import get_accuracy_metrics
from df_utils import append_to_df




def extract_features_and_targets(df, target_id):
    
    #copy to keep original df clean (as key-based assignment performs side-effects)
    temp_df = df.copy()
    
    #features engineering:
    
    temp_df['lag_1'] = temp_df[target_id].shift(1)
    temp_df['lag_2'] = temp_df[target_id].shift(2)
    temp_df['lag_3'] = temp_df[target_id].shift(3)
    temp_df['lag_4'] = temp_df[target_id].shift(4)
    temp_df['rolling_mean'] = temp_df[target_id].rolling(window=7).mean()
    temp_df['expanding_mean'] = temp_df[target_id].expanding(2).mean()
    
    temp_df['Date'] = temp_df.index

    min_time = min(temp_df['Date'])
    
    f1, f2, f3 = [], [], []
    for index, row in temp_df.iterrows():
        f1.append((row['Date'] - min_time).total_seconds())
        #sinusoidal date encoding
        f2.append(np.sin(row['Date'].month / 12 * np.pi))
        #cosinusoidal date encoding
        f3.append(np.cos(row['Date'].month / 12 * np.pi))
    
    temp_df['f1'] = f1
    temp_df['f2'] = f2
    temp_df['f3'] = f3
    
    temp_df = temp_df.dropna()
    
    #X
    features =  temp_df[["f1", "f2", "f3", "lag_1","lag_2", "lag_3", "lag_4", "rolling_mean", "expanding_mean"]] #features = temp_df[temp_df.columns.drop(target_id, "Date")] #all columns but targetId are features     #features =  temp_df[["f1", "f2", "f3"]
    #y
    targets = temp_df[target_id]

    return features, targets


def extract_features(df, target_id):
    return extract_features_and_targets(df, target_id)[0]


def make_one_step_forecast(fitted, history, target_id):
    last_date = history.tail(1).index[0]
    next_date = get_next_date(last_date)
    
    history = append_to_df(history, next_date, [])

    X = extract_features(history, target_id)
    next_date_features = X.tail(1)

    one_step_forecast = fitted.predict(next_date_features)[0]
    return next_date, one_step_forecast


def regressor_rolling_norefit(fitted, history, target_id, horizon):
    forecasts = []
    
    for t in range(horizon):
        one_step_datetime, one_step_forecast = make_one_step_forecast(fitted, history, target_id)
        forecasts.append(one_step_forecast)
        history = append_to_df(history, one_step_datetime, {target_id: one_step_forecast})         #appending to df

    return np.asarray(forecasts)


"""
Meta-regressor made of 2 regressors, the second of which trains on the 
residuals of the first. It extends from sklearn's BaseEstimator, 
RegressorMixin classes so that it can be analyzed the same as a sklearn
regressor, leveraging the utilities already available for it (grid-search,
TimeSeriesSplit etc.)
"""
class StackingMetaRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, base, residual):
        self.base = base
        self.residual = residual

    def fit(self, X, y):
        self.base.fit(X, y)
        self.residual.fit(X, y - self.base.predict(X))
        return self

    def predict(self, X):
        return self.base.predict(X) + self.residual.predict(X)


def optimize_timeseries_regressor_hyperparams(Xtrain, ytrain, regressor, scoring='neg_mean_absolute_percentage_error', display_info = False):
    cv = TimeSeriesSplit(n_splits = 10, max_train_size = None, test_size = None, gap = 0)
    
    reg_name, model, param_grid = regressor
    gsearch = GridSearchCV(estimator = model, cv = cv, param_grid = param_grid, scoring = scoring)
    
    n_scores = cross_val_score(estimator = gsearch, X = Xtrain, y = ytrain, scoring=scoring, cv=cv, n_jobs=-1, error_score='raise') #n_jobs=-1 for using all processors
    
    if display_info:
        print('crossval mape for ' + reg_name +': ' + str(-np.mean(n_scores)))
    
    return gsearch.fit(Xtrain, ytrain).best_estimator_


def plot(actual, forecasted, model_name):
    fig = plt.figure()    #plt.figure(figsize = (20,10))
    fig.suptitle(model_name + ' on test data')
    plt.plot(actual, label = 'actual')
    plt.plot(forecasted, label = 'forecasted')
    plt.plot(np.abs(forecasted - actual), label = 'absolute error')
    plt.legend(loc='upper left', fontsize=13)


def get_best_regressor_from_all(df, TARGETID, test_cardinality, regressors):
    best_mape, best_model, best_metrics = float("inf"), regressors[0][0], None
    
    #trainval-test split
    X, y = extract_features_and_targets(df, TARGETID)
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size = test_cardinality, shuffle = False)      #print('features extracted are: ') ; print(X)

    #model evaluation
    for regressor in regressors:

        best_of_this_regressor = optimize_timeseries_regressor_hyperparams(Xtrain, ytrain, regressor, scoring = 'neg_mean_absolute_percentage_error')
        
        fitted = best_of_this_regressor.fit(Xtrain, ytrain)
        Xytrain, Xytest = train_test_split(df, test_size = test_cardinality, shuffle = False) 
        predicty = regressor_rolling_norefit(fitted, Xytrain, TARGETID, test_cardinality)
        
        plot(ytest.to_numpy(), predicty, regressor[0])
        
        metrics = get_accuracy_metrics(ytest, predicty)

        if metrics["mape"] < best_mape:
            best_mape, best_model, best_metrics = metrics["mape"], best_of_this_regressor, metrics #save best model for out-of-sample pred
            
    return best_model, best_metrics


def pre_log_y(model):
    return TransformedTargetRegressor(regressor = model, func = np.log, inverse_func = np.exp)


def forecast_stock_series(time_series_filename, forecast_horizon, test_cardinality):

    df = pd.read_csv("../assets/" + time_series_filename, sep=';', decimal=',')

    index_id = time_series_filename[:-len('.csv')]

    df['Dates'] = df['Dates'].apply(pd.to_datetime)
    
    df = df.set_index('Dates')
    

    #HYPER-PARAMETERS
    #stacking linear + Extra-trees:
    sle_param_grid = dict()

    sle_param_grid['residual__n_estimators'] = [10, 50, 100, 500, 1000, 5000]

    #max levels in tree
    sle_param_grid['residual__max_depth'] = [int(x) for x in np.linspace(10, 50, num = 5)]

    #min samples required to split an internal node
    sle_param_grid['residual__min_samples_split'] = [2, 5, 10]
    
    #min samples required at each leaf node
    sle_param_grid['residual__min_samples_leaf'] = [1, 2, 4]
    
    #enable or not bootstrapping for selecting samples for training each tree
    sle_param_grid['residual__bootstrap'] = [True, False]
    
    #features to consider at every split
    sle_param_grid['residual__max_features'] = ['auto', 'sqrt']
    
    
    #stacking linear + ADABOOST + decision trees
    slad_param_grid = dict()
    
    slad_param_grid['residual__n_estimators'] = [10, 50, 100, 500, 1000, 5000]

    slad_param_grid['residual__learning_rate'] = [i for i in np.arange(0.1, 2.1, 0.1)]

    #max levels in tree
    slad_param_grid['residual__base_estimator__max_depth'] = [int(x) for x in np.linspace(10, 50, num = 5)]

    #min samples required to split an internal node
    slad_param_grid['residual__base_estimator__min_samples_split'] = [2, 5, 10]
    
    #min samples required at each leaf node
    slad_param_grid['residual__base_estimator__min_samples_leaf'] =  [1, 2, 4]
    
    #enable or not bootstrapping for selecting samples for training each tree
    slad_param_grid['residual__base_estimator__bootstrap'] = [True, False]
    
    #features to consider at every split
    slad_param_grid['residual__base_estimator__max_features'] = ['auto', 'sqrt']
    

    regressors = [ ('StackLinAdaRF',
                      StackingMetaRegressor(LinearRegression(),
                                  AdaBoostRegressor(base_estimator = 
                                                    RandomForestRegressor(n_estimators= 5,
                                                       criterion= 'mse',
                                                       max_features = 'sqrt',
                                                       min_samples_split = 3,
                                                       random_state = 40))), {}),
                  ('StackLinAdaRF',
                   StackingMetaRegressor(LinearRegression(),
                                         AdaBoostRegressor()), {}),
                  ('StackLinRF',
                   StackingMetaRegressor(LinearRegression(),
                                         RandomForestRegressor()), {}),
                  ('StackLinET',
                   StackingMetaRegressor(LinearRegression(),
                                         ExtraTreesRegressor()), sle_param_grid),
                  ('StackLinAdaDT',
                   StackingMetaRegressor(LinearRegression(),
                                         AdaBoostRegressor()), slad_param_grid)]
    


    model, accuracy_metrics = get_best_regressor_from_all(df, index_id, test_cardinality, regressors)
    
    print('best model for '+ str(index_id) + ': '+ str(model) +" with MAPE: " + str(accuracy_metrics["mape"]))
    




if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    
    forecast_horizon = 261      #forecast: 1 year = 261(2021)
    test_cardinality = 180      #test: 1 year = 180 (2020)

    
    time_series_filenames = ["S&P_500_INDEX.csv", "U.S._Treasury.csv","MSCI_EM.csv", "MSCI_EURO.csv", "GOLD_SPOT_$_OZ.csv", "FTSE_MIB_INDEX.csv", "All_Bonds_TR.csv"]

    for filename in time_series_filenames:
        forecast_stock_series(filename, forecast_horizon, test_cardinality)