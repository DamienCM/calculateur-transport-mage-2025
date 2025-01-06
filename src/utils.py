from functools import cache, lru_cache
from itertools import chain, combinations
import numpy as np 



@cache
def partitions_count(n, k=0): 
    # checks if n is integer and n is greater than 0
    if n < 0:
        raise ValueError(f"n must be a positive integer type n = {type(n)}")
    return int(n < 1) or k*partitions_count(n-1, k) + partitions_count(n-1, k+1)

# tarif_par_kg = {}
# def set_new_tarif(new_tarif):
#     global tarif_par_kg
#     tarif_par_kg = new_tarif

# @lru_cache
# def tarif_par_masse(masse):
#     global tarif_par_kg
#     if masse in tarif_par_kg:
#         return tarif_par_kg[masse]
#     else:
#         return tarif_par_kg[max(tarif_par_kg.keys())]


def find_best_config2():
    return 0


weights = []
prices = []
def set_new_tarif(new_weights, new_prices):
    global weights, prices
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

def partitions_array(elements):
    """
    Generate all possible partitions of a given set.

    :param elements: Numpy array of elements (e.g., np.array([1, 3, 5])).
    :return: List of partitions, each partition being a list of sub-arrays.
    """
    if len(elements) == 0:
        return [[]]  # Base case: empty partition for an empty set

    first = elements[0]
    rest = elements[1:]
    rest_partitions = partitions_array(rest)

    all_partitions = []
    for partition in rest_partitions:
        # Add 'first' to each existing sub-array
        for i in range(len(partition)):
            new_partition = partition[:i] + [np.append(partition[i], first)] + partition[i+1:]
            all_partitions.append(new_partition)
        # Add 'first' as a new sub-array
        all_partitions.append([np.array([first])] + partition)

    return all_partitions


def partitions_list_numpy(elements):
    """
    Generates all partitions of a given set using NumPy arrays.

    :param elements: NumPy array of elements (e.g., np.array([1, 3, 5])).
    :return: NumPy array of partitions, preallocated to fit all possible partitions.
    """
    # if elements is a list convert it to np array
    if type(elements) is list:
        elements = np.array(elements)
    if type(elements) is not np.ndarray:
        raise ValueError("Input must be a NumPy array")
    n = len(elements)
    total_partitions = partitions_count(n)
    if total_partitions is None:
        raise ValueError("Partitions count not precomputed for this size. Extend the Bell numbers computation.")

    # Preallocate output array (partitions, groups, elements)
    output = np.zeros((total_partitions, n, n), dtype=object)

    def recursive_partition(subset):
        if subset.size == 0:
            return [[]]  # Base case: empty set has one partition

        first = subset[0]
        rest = subset[1:]
        rest_partitions = recursive_partition(rest)

        all_partitions = []
        for partition in rest_partitions:
            # Add 'first' to each existing subset
            for i, group in enumerate(partition):
                new_partition = partition[:i] + [np.append(group, first)] + partition[i+1:]
                all_partitions.append(new_partition)

            # Add 'first' as a new subset
            all_partitions.append([[first]] + partition)

        return all_partitions

    # Generate all partitions
    all_partitions = recursive_partition(elements)

    # Populate the preallocated output array
    for idx, partition in enumerate(all_partitions):
        for group_idx, group in enumerate(partition):
            output[idx, group_idx, :len(group)] = group

    return output


if __name__ == '__main__':
    elements = [1,2,3,4]
    if 0:
        print(f"Partitions count: {partitions_count(len(elements))}")
        print("Partitions:")
        i=0
        for partition in find_best_config(elements):
            i+=1
            print(f"{i}: {partition}")

    if 1:
        print (partitions_list_numpy(np.array(elements)))