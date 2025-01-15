import ctypes
import numpy as np
from pathlib import Path

# Compile the C code
import subprocess
subprocess.run(['gcc', '-fPIC', '-shared', '-o', 'libpartition_optimizer.so', 'partition_optimizer.c'])

# Load the compiled library
lib = ctypes.CDLL(str(Path.cwd() / 'bin/libpartition_optimizer.so'))

# Define the Result structure in Python
class OptimizationResult(ctypes.Structure):
    _fields_ = [
        ("price", ctypes.c_double),
        ("num_subsets", ctypes.c_int),
        ("subsets", ctypes.POINTER(ctypes.POINTER(ctypes.c_double))),
        ("subset_sizes", ctypes.POINTER(ctypes.c_int))
    ]

# Define argument types and return types
lib.set_new_tarif.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64),
    np.ctypeslib.ndpointer(dtype=np.float64),
    ctypes.c_int
]

lib.find_best_config.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64),
    ctypes.c_int
]
lib.find_best_config.restype = ctypes.POINTER(OptimizationResult)

# Define cleanup function type
lib.cleanup_result.argtypes = [ctypes.POINTER(OptimizationResult)]

# Function to convert C result to Python format
def convert_result_to_python(c_result):
    if not c_result:
        return None
    
    result = {
        'price': c_result.contents.price,
        'config': []
    }
    
    # Convert subsets to Python lists
    for i in range(c_result.contents.num_subsets):
        subset = []
        for j in range(c_result.contents.subset_sizes[i]):
            subset.append(c_result.contents.subsets[i][j])
        result['config'].append(subset)
    
    return result

# Wrapper functions
def set_new_tarif(new_weights, new_prices, max_weight):
    for i in range(len(new_weights)):
        if new_weights[i] > max_weight : 
            new_prices[i] =  float('inf') 
    lib.set_new_tarif(
        np.array(new_weights, dtype=np.float64),
        np.array(new_prices, dtype=np.float64),
        len(new_weights)
    )

def find_best_config(elements):
    elements_arr = np.array(elements, dtype=np.float64)
    c_result = lib.find_best_config(elements_arr, len(elements))
    
    if not c_result:
        raise RuntimeError("Optimization failed")
    
    # Convert C result to Python format
    result = convert_result_to_python(c_result)
    
    # Clean up C memory using our cleanup function
    lib.cleanup_result(c_result)
    
    return result

# # Example usage
# weights = [1.0, 2.0, 3.0, 4.0, 5.0]
# prices = [10.0, 15.0, 20.0, 25.0, 30.0]
# set_new_tarif(weights, prices)

# elements = [1.5, 2.5, 3.5]
# result = find_best_config(elements)
# print(f"Best price: {result['price']}")
# print(f"Configuration: {result['config']}")