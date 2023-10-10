# -*- coding: utf-8 -*-

import os
import numpy as np
import random as rd
from abc import  abstractmethod, ABCMeta

from forecast_arima import forecast_index
from fhs import filtered_historical_simulation 
from whs import volatility_weighted_historical_simulation, prepare_for_whs
from caching import enable_nparray_cache, enable_shelve_cache
from json_utils import from_json_file_to_dict, from_dict_to_json_file,from_json_file_to_dict_of_dicts_of_numpy, from_dict_of_dicts_of_numpy_to_json_file




class ProfitsFunction:
    """
    Computes a profits measure that will be combined with a risk measure
    to produce the fitness of a portfolio solution. It averages the profits/
    losses of the last forecast_horizon // 3 closing prices forecasts.
    """
    def __init__(self, data, forecast_horizon, forecasts_dir_path, display = False):
        self.data = data
        self.forecast_horizon = forecast_horizon
        #folder where resides cache of forecasts
        self.forecasts_dir_path = forecasts_dir_path
        self.profits = {}
        #window along with average the profits
        self.window = forecast_horizon // 3
        self.display = display


    def init(self):
        if self.display:
            print('computing profits...')
        
        #generate profits table
        for asset in self.data.keys():
            forecast_file_name = 'forecast_hz'+ str(self.forecast_horizon) + '_' + asset + '.json'
            
            #check if already saved as a file and if yes only read it
            asset_forecast_file_name = self.forecasts_dir_path + forecast_file_name

            if os.path.isfile(asset_forecast_file_name):
                if self.display:
                    print("   cache present... => retrieving from it")
                forecasts_dict = from_json_file_to_dict(asset_forecast_file_name)
                forecasts_prices = np.asarray(list(forecasts_dict["text"].values()))
            else:
                if self.display:
                    print("   cache not present.. => compute")
                forecast_obj = forecast_index(asset + '.csv', self.forecast_horizon)
                from_dict_to_json_file(forecast_obj.__dict__, asset_forecast_file_name)
                forecasts_prices = np.asarray(list(forecast_obj.text.values()))
            
            #translate from prices to profits
            forecasted_profits = forecasts_prices - forecasts_prices[0]
            #get profits as the mean (for every asset) of a window of last forecasted profits
            self.profits[asset] = np.mean(forecasted_profits[-self.window:])
            
            if self.display:
                print('asset '+ str(asset) + ' done.')
                
        if self.display:
            print('...done')
        
    def compute(self, candidate):
        global_profit = np.dot(np.array(list(self.profits.values())), candidate)
        return global_profit


class RiskFunction(object, metaclass = ABCMeta):
    """
    Abstract class with behaviour common to VarRiskFunctions (subclasses
    compute risk with FHS or VWHS).
    """
    
    def __init__(self, data, forecast_horizon, std_returns_dir_path, display = False):
        self.data = data
        self.forecast_horizon = forecast_horizon
        #historical simulation parameters
        self.sample_size = 250
        self.drawings_count = 2000
        #folder where resides cache of value-at-risk values
        self.std_returns_dir_path = std_returns_dir_path
        self.display = display
        
    def init(self):
        if self.display:
            print("standardizing returns for VaR computation...")

        if os.path.isfile(self.std_returns_dir_path):
            if self.display:
                print("   cache present... => retrieving from it")
            
            mydict = from_json_file_to_dict_of_dicts_of_numpy(self.std_returns_dir_path)
            self.iid_sample = mydict["iid_sample"]
            self.tomorrow_volatility = mydict["tomorrow_volatility"]
        else:
            if self.display:
                print("   cache not present.. => compute")
            
            self.iid_sample, self.tomorrow_volatility = prepare_for_whs(self.data, self.sample_size)
            from_dict_of_dicts_of_numpy_to_json_file(dict(iid_sample =  self.iid_sample, 
                                                          tomorrow_volatility = self.tomorrow_volatility), self.std_returns_dir_path)
        if self.display:
            print("... done")
    
    @abstractmethod
    def compute(self, candidate):
        pass
    
    
class FhsVarRiskFunction(RiskFunction):
    """
    Computes a risk measure that will be combined with a profits measure
    to produce the fitness of a portfolio solution. It computes the risk
    based on value-at-risk value obtained with Filtered Historical 
    Simulation methodology.
    """
    
    """
    Since the computational time needed for FHS calculation a disk cache
    is adopted as to cache results computed on different runs.
    """
    @enable_shelve_cache("fhs_var_cache.txt")
    def compute(self, candidate):
        risk = filtered_historical_simulation(data = self.data,
                                                         iid_sample = self.iid_sample,
                                                         forecast_horizon = self.forecast_horizon,
                                                         drawings_count = self.drawings_count,
                                                         weight_array = candidate)["1%"]
        #dimensionality adjustment
        risk/= 50
        return risk



class WhsVarRiskFunction(RiskFunction):
    """
    Computes a risk measure that will be combined with a profits measure
    to produce the fitness of a portfolio solution. It computes the risk
    based on value-at-risk value obtained with Volatility Weighted Historical 
    Simulation methodology.
    """
    def compute(self, candidate):
        risk = volatility_weighted_historical_simulation(data = self.data,
                                                         iid_sample = self.iid_sample,
                                                         tomorrow_volatility = self.tomorrow_volatility,
                                                         forecast_horizon = self.forecast_horizon,
                                                         drawings_count = self.drawings_count,
                                                         weight_array = candidate)["1%"]
        #dimensionality adjustment
        risk/= 50
        return risk


def round_to_nearest_half(x, base = 0.05):
     return round(base*round(x / base), 2)
 
def round_array_to_nearest_half_summing_to_one(old_array):
    array = old_array.copy()
    ran_index = rd.randint(0, len(array)-1)
    array_partial_sum = 0
    for i in range(len(array)):
        if i != ran_index:
            array[i] = round_to_nearest_half(array[i])
            array_partial_sum += array[i]
    array[ran_index] = 1 - array_partial_sum

    return array

def normalize(old_array):
    return np.abs(old_array) / np.sum(np.abs(old_array))



class Profits_RiskFunction:
    """
    Combines a profits measure with a risk measure to produce the fitness of 
    a portfolio solution. It contains the constraints of the portfolio
    optimization problem.
    """
    def __init__(self, profits_function, risks_function):
        self.profits_function = profits_function
        self.risks_function = risks_function
    
    def init(self):
        self.profits_function.init()
        self.risks_function.init()
    
    def compute(self, candidate):
        p = self.profits_function.compute(candidate)
        r = self.risks_function.compute(candidate)
        return 1.2 * p + 0.8 * r

    #constraints: 
    def check_valid(self, candidate):
        #not weight's sum > 1
        weight_sum_valid = candidate.sum() <= 1
        
        #not asset_weight < 0.05
        single_weigth_valid = not np.any(candidate < 0.05) 
        
        return weight_sum_valid and single_weigth_valid
    
    def normalize(self, candidate):
        return round_array_to_nearest_half_summing_to_one(normalize(candidate))


class Profits_WhsVarRiskFunction(Profits_RiskFunction):
    """
    Profits_RiskFunction subclass that outputs fitness combining profits and
    value-at-risk resulting from Volatility Weighted Historical Simulation
    as risk metric.
    """
    def __init__(self, data, forecast_horizon, forecasts_dir_path, std_returns_dir_path):
        profits_function = ProfitsFunction(data, forecast_horizon, forecasts_dir_path)
        risks_function = WhsVarRiskFunction(data, forecast_horizon, std_returns_dir_path)
   
        super(Profits_WhsVarRiskFunction, self).__init__(profits_function, risks_function)

class Profits_FhsVarRiskFunction(Profits_RiskFunction):
    """
    Profits_RiskFunction subclass that outputs fitness combining profits and
    value-at-risk resulting from Filtered Historical Simulated as risk metric.
    """
    def __init__(self, data, forecast_horizon, forecasts_dir_path, std_returns_dir_path):
        profits_function = ProfitsFunction(data, forecast_horizon, forecasts_dir_path)
        risks_function = FhsVarRiskFunction(data, forecast_horizon, std_returns_dir_path)
   
        super(Profits_FhsVarRiskFunction, self).__init__(profits_function, risks_function)


@enable_nparray_cache(maxsize=None)
def evaluate_fitness(candidate, function_obj):
    fitness = -1
    if function_obj.check_valid(candidate):
        fitness = function_obj.compute(candidate)
    return fitness


def differential_evolution_optimize(
        function_obj,
        n_dimensions,
        max_iter = 1000,
        f_factor = 0.9,
        cr_ratio = 0.5,
        pop_size = 100,
        min_value_for_variable = 0,
        max_value_for_variable = 100,
        display = False):
    
    current_iter = 0
    
    
    old_population = [np.random.randint(min_value_for_variable, 
                                        max_value_for_variable, 
                                        size = n_dimensions) for x in range(0, pop_size)]       #old_population = [my_generate_random_solution(n_assets) for x in range(0, pop_size)]

    old_population = [function_obj.normalize(x) for x in old_population]
    
    population = old_population
    
    while current_iter < max_iter:
        
        new_population = []
        
        for candidate in population:
            
            another_candidate, father, mother = rd.sample(population, 3)
            
            #mutation
            modified_candidate = another_candidate + (father - mother) * f_factor

            modified_candidate = function_obj.normalize(modified_candidate)
            
            random_num = rd.randint(0, n_dimensions - 1)
            
            #crossover
            intermediate_candidate = np.array([modified_candidate[i] if rd.random() > cr_ratio or random_num == i else candidate[i] for i in range(len(candidate))])
            
            intermediate_candidate = function_obj.normalize(intermediate_candidate)

            #selection
            new_member = intermediate_candidate if evaluate_fitness(intermediate_candidate, function_obj) > evaluate_fitness(candidate, function_obj) else candidate

            new_population.append(new_member)

        population = new_population

        current_iter += 1
        
        if display:

            best_member = sorted(population, key = lambda candidate: evaluate_fitness(candidate, function_obj))[-1]
        
            print('it : ' + str(current_iter) + '/'+ str(max_iter)+': b.m.: '+ str(best_member) + ' w. fitn: ' + str(evaluate_fitness(best_member, function_obj)))
     
    best_member = sorted(population, key = lambda candidate: evaluate_fitness(candidate, function_obj))[-1]

    if display:
        print("best_member: "+ str(best_member)+ " w. fitness: " + str(evaluate_fitness(best_member, function_obj)))

    return best_member