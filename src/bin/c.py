"""
Python interface for the partition optimizer C library.

This module provides a high-level Python interface to a C library that performs
partition optimization. It handles memory management, type conversion, and provides
a Pythonic API for the underlying C functions.

The optimizer finds the optimal way to partition a set of elements into subsets
based on predefined weights and prices, typically used for optimizing shipping
or packaging configurations.

Example:
    >>> weights = [1.0, 2.0, 3.0, 4.0, 5.0]
    >>> prices = [10.0, 15.0, 20.0, 25.0, 30.0]
    >>> set_new_tarif(weights, prices, max_weight=10.0)
    >>> elements = [1.5, 2.5, 3.5]
    >>> result = find_best_config(elements)
    >>> print(f"Best price: {result['price']}")
    >>> print(f"Configuration: {result['config']}")
"""

import ctypes
import numpy as np
from pathlib import Path
import sys 
import os

# Compile the C code into a shared library
import subprocess

def get_base_path():
    # Check if running as PyInstaller executable
    if getattr(sys, 'frozen', False):
        # When running as PyInstaller bundle
        return os.path.join(sys._MEIPASS, 'bin')
        # return os.path.join(sys._MEIPASS, '_internal', 'bin')
    else:
        # When running as standard Python script
        return os.path.dirname(os.path.abspath(__file__))

def compile_c_library():
    base_path = get_base_path()
    
    source_file = os.path.join(base_path, 'partition_optimizer.c')
    output_file = os.path.join(base_path, 'libpartition_optimizer.so')
    
    try:
        result = subprocess.run(
            ['gcc', '-fPIC', '-shared', '-o', output_file, source_file],
            capture_output=True,
            text=True,
            check=True  # This will raise CalledProcessError if gcc fails
        )
        return True, output_file
    except subprocess.CalledProcessError as e:
        print(f"GCC compilation failed with error:\n{e.stderr}")
        return False,None
    except FileNotFoundError:
        print("GCC compiler not found. Please ensure GCC is installed and in PATH")
        return False,None
# Load the compiled library from the bin directory
#Std exec 

result,lib = compile_c_library()
lib = ctypes.CDLL(str(lib))


class OptimizationResult(ctypes.Structure):
    """
    Python representation of the C struct for optimization results.
    
    Fields:
        price (float): Total price of the optimal configuration
        num_subsets (int): Number of subsets in the optimal partition
        subsets (pointer): Pointer to array of arrays containing the elements
        subset_sizes (pointer): Pointer to array containing size of each subset
    """
    _fields_ = [
        ("price", ctypes.c_double),
        ("num_subsets", ctypes.c_int),
        ("subsets", ctypes.POINTER(ctypes.POINTER(ctypes.c_double))),
        ("subset_sizes", ctypes.POINTER(ctypes.c_int))
    ]

# Define C function signatures for type checking
lib.set_new_tarif.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64),  # weights array
    np.ctypeslib.ndpointer(dtype=np.float64),  # prices array
    ctypes.c_int  # array length
]

lib.find_best_config.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64),  # elements array
    ctypes.c_int  # array length
]
lib.find_best_config.restype = ctypes.POINTER(OptimizationResult)

lib.cleanup_result.argtypes = [ctypes.POINTER(OptimizationResult)]

def convert_result_to_python(c_result):
    """
    Convert C optimization result to Python dictionary format.
    
    Args:
        c_result (ctypes.POINTER(OptimizationResult)): Pointer to C result structure
        
    Returns:
        dict: Dictionary containing:
            - 'price': float, total price of the configuration
            - 'config': list of lists, each sublist represents a subset of elements
            
    Returns None if c_result is NULL.
    """
    if not c_result:
        return None
    
    result = {
        'price': c_result.contents.price,
        'config': []
    }
    
    # Convert C arrays of subsets to Python lists
    for i in range(c_result.contents.num_subsets):
        subset = []
        for j in range(c_result.contents.subset_sizes[i]):
            subset.append(c_result.contents.subsets[i][j])
        result['config'].append(subset)
    
    return result

def set_new_tarif(new_weights, new_prices, max_weight):
    """
    Set new weight-price combinations for the optimization algorithm.
    
    Args:
        new_weights (list[float]): List of weights for different configurations
        new_prices (list[float]): List of prices corresponding to the weights
        max_weight (float): Maximum allowed weight per subset
        
    Notes:
        - Lists must be of equal length
        - Configurations exceeding max_weight will have their price set to infinity
        - This must be called before find_best_config
    
    Raises:
        ValueError: If input lists have different lengths
    """
    if len(new_weights) != len(new_prices):
        raise ValueError("Weights and prices lists must have the same length")
    
    # Set price to infinity for configurations exceeding max weight
    for i in range(len(new_weights)):
        if new_weights[i] > max_weight:
            new_prices[i] = float('inf')
    
    lib.set_new_tarif(
        np.array(new_weights, dtype=np.float64),
        np.array(new_prices, dtype=np.float64),
        len(new_weights)
    )

def find_best_config(elements):
    """
    Find the optimal partition configuration for a given set of elements.
    
    Args:
        elements (list[float]): List of element weights to be partitioned
        
    Returns:
        dict: Dictionary containing:
            - 'price': float, total price of the optimal configuration
            - 'config': list of lists, each sublist contains the elements in one subset
            
    Raises:
        RuntimeError: If the optimization fails
        ValueError: If elements list is empty
    """
    if not elements:
        raise ValueError("Elements list cannot be empty")
    
    elements_arr = np.array(elements, dtype=np.float64)
    c_result = lib.find_best_config(elements_arr, len(elements))
    
    if not c_result:
        raise RuntimeError("Optimization failed")
    
    # Convert C result to Python format
    result = convert_result_to_python(c_result)
    
    # Clean up C memory
    lib.cleanup_result(c_result)
    
    return result

# Example usage (commented out)
# weights = [1.0, 2.0, 3.0, 4.0, 5.0]
# prices = [10.0, 15.0, 20.0, 25.0, 30.0]
# set_new_tarif(weights, prices, max_weight=10.0)
# 
# elements = [1.5, 2.5, 3.5]
# result = find_best_config(elements)
# print(f"Best price: {result['price']}")
# print(f"Configuration: {result['config']}")