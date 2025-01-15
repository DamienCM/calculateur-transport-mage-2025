print("Loading functools : ...")
from functools import cache, lru_cache
print("Loading functools : DONE")
print("Loading numpy : ...")
import numpy as np 
print("Loading numpy : DONE")

@cache
def partitions_count(n, k=0): 
    # checks if n is integer and n is greater than 0
    if n < 0:
        raise ValueError(f"n must be a positive integer type n = {type(n)}")
    return int(n < 1) or k*partitions_count(n-1, k) + partitions_count(n-1, k+1)

weights = []
prices = []
def set_new_tarif(new_weights, new_prices, max_weight):
    global weights, prices
    for i in range(len(new_weights)):
        if new_weights[i] > max_weight : 
            new_prices[i] =  float('inf') 
    weights = new_weights
    prices = new_prices

@lru_cache(maxsize=None)

def tarif_par_masse(masse):
    if masse <= weights[-1]:
        return prices[np.searchsorted(weights, masse, side='right') - 1]
    else:
        return prices[-1]  # Use the maximum price for weights above the highest threshold
# @lru_cache(maxsize=None)
def find_best_config(elements, i=0, price=0):
    """
    List all partitions and finds the best partition with corresponding price
    
    :param elements: Masses of articles to send
    :return: price, config
    """
    if elements == []:
        return [[]]  # Cas de base : partition vide pour un ensemble vide

    first = elements[0]
    rest = elements[1:]
    rest_partitions = find_best_config(rest, i+1)
    all_partitions = []
    counter = 0
    if i == 0 :
        best_price = float('inf')
        best_config = []
    for partition in rest_partitions:
        # Ajouter 'first' à chaque sous-ensemble existant
        for j in range(len(partition)):
            new_partition = partition[:j] + [partition[j] + [first]] + partition[j+1:]
            if i==0:
                counter+=1
                # print(f"{new_partition=}")
                mass = [sum(subset) for subset in new_partition]
                price = sum([tarif_par_masse(masse) for masse in mass])
                if price < best_price:
                    best_price = price
                    best_config = new_partition
                continue
            all_partitions.append(new_partition)
        # Ajouter 'first' comme nouveau sous-ensemble
        new_partition=[[first]] + partition
        if i==0:
            # print(f"{new_partition=}")
            counter+=1
            mass = [sum(subset) for subset in new_partition]
            price = sum([tarif_par_masse(masse) for masse in mass])
            if price < best_price:
                best_price = price
                best_config = new_partition
        all_partitions.append(new_partition)
    if i==0:
        print(f'counter={counter}')
        return best_price,best_config
    return all_partitions
