# -*- coding: utf-8 -*-


import numpy as np

from whs import read_indexes
from genetic_algo import Profits_WhsVarRiskFunction, evaluate_fitness


class PsoParticle:
    def __init__(self, position, velocity, pbest, gbest):
        self.position = position
        self.velocity = velocity
        self.pbest = pbest
        self.gbest = gbest


def pso_optimize(function_obj,
                 n_dimensions,
                 max_iter = 1000,
                 pop_size = 100,
                 c1 = 2.0,
                 c2 = 2.0,
                 min_value_for_variable = 0,
                 max_value_for_variable = 100,
                 display = False):
    
    positions = [np.random.randint(min_value_for_variable, 
                                   max_value_for_variable, 
                                   size = n_dimensions) for i in range(0, pop_size)]
    
    positions = [function_obj.normalize(position) for position in positions]
    
    gbest = sorted(positions, key = lambda position : evaluate_fitness(position, 
                                                                       function_obj))[-1]
    population = [PsoParticle(pbest = position,
                               gbest = gbest,
                               position = position,
                               velocity = 0) for position in positions]#paper suggests to initialize velocitiesy near to or actually 0
   
    current_iter = 0
    
    while current_iter < max_iter:
    
        for particle in population:
            
            r1, r2 = np.random.random(2)
            
            particle.velocity = particle.velocity + c1 * r1 * (particle.pbest - particle.position) + c2 * r2 * (particle.gbest - particle.position)
            
            not_normalized_position = particle.position + particle.velocity
            
            particle.position = function_obj.normalize(not_normalized_position)
            
            new_particle_fitness = evaluate_fitness(particle.position, function_obj)
            
            if  new_particle_fitness > evaluate_fitness(particle.pbest,  function_obj):
                particle.pbest = particle.position
                if new_particle_fitness > evaluate_fitness(particle.gbest,  function_obj):
                    particle.gbest = particle.position
                    
        if display:         
            print('it : ' + str(current_iter)+'/'+ str(max_iter) +' best s: ' + str(population[0].gbest) + ' w fitn: '+str(evaluate_fitness(population[0].gbest, function_obj)))
        
        current_iter += 1
        
    gbest = population[0].gbest
    
    if display:
        print('pso gbest:' + str(gbest))
        
    return gbest







if __name__ == '__main__':
    
    assets = ["S&P_500_INDEX.csv", "U.S._Treasury.csv" ,"MSCI_EM.csv", "MSCI_EURO.csv", "GOLD_SPOT_$_OZ.csv", "FTSE_MIB_INDEX.csv", "All_Bonds_TR.csv"]
    
    forecasts_dir_path = '../forecasts/'
    std_returns_file_path = '../std_returns/std_returns.json'

    forecast_horizon = 261
    
    time_series = read_indexes(assets)
    
    function_obj = Profits_WhsVarRiskFunction(data = time_series, 
                                              forecast_horizon = forecast_horizon, 
                                              forecasts_dir_path = forecasts_dir_path,
                                              std_returns_dir_path = std_returns_file_path)

    function_obj.init()


    optimum_sol = pso_optimize(function_obj,
                               n_dimensions = len(assets),
                               max_iter = 100,
                               pop_size = 100,
                               c1 = 2.0,
                               c2 = 2.0,
                               display = True)
    
    portfolio_dict = dict(zip(assets, optimum_sol))
    
    print(portfolio_dict)
    