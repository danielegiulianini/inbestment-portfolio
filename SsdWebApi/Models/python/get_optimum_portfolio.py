import json, os
import numpy as np

from whs import read_indexes
from genetic_algo import Profits_WhsVarRiskFunction, differential_evolution_optimize
from json_utils import from_dict_to_json_file, from_json_file_to_dict


def compute_optimum_portfolio(assets, forecast_horizon, forecasts_dir_path, std_returns_dir_path):
        
    time_series = read_indexes(assets)
    
    function_obj = Profits_WhsVarRiskFunction(data = time_series, 
                                              forecast_horizon = forecast_horizon, 
                                              forecasts_dir_path = forecasts_dir_path, 
                                              std_returns_dir_path = std_returns_dir_path)
    
    function_obj.init()

    optimum_sol = differential_evolution_optimize(function_obj,
                                                  n_dimensions = len(assets),
                                                  max_iter = 100,
                                                  f_factor = 0.9,
                                                  cr_ratio = 0.5,
                                                  pop_size = 100,
                                                  display = False)
    
    portfolio_dict = dict(zip(assets, np.round(optimum_sol, 2)))    
    
    return portfolio_dict



if __name__ == '__main__':
    
    assets = ["S&P_500_INDEX.csv", "U.S._Treasury.csv" ,"MSCI_EM.csv", "MSCI_EURO.csv", "GOLD_SPOT_$_OZ.csv", "FTSE_MIB_INDEX.csv", "All_Bonds_TR.csv"]

    forecasts_dir_path = '../forecasts/'
    
    std_returns_dir_path = '../std_returns/std_returns.json'
    
    portfolio_output_path = '../optimum_portfolio/optimum_portfolio.json'
    
    portfolio_dict = {}
    if os.path.isfile(portfolio_output_path):
        portfolio_dict = from_json_file_to_dict(portfolio_output_path)
    else:
        forecast_horizon = 261  #forecast: 1 year = 261(2021)
        portfolio_dict = compute_optimum_portfolio(assets, 
                                                   forecast_horizon,
                                                   forecasts_dir_path, 
                                                   std_returns_dir_path)  
    print(json.dumps(portfolio_dict))
    
    from_dict_to_json_file(portfolio_dict, portfolio_output_path)
