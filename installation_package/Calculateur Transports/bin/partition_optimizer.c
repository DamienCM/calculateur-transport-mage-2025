#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <string.h>

// Global variables
double* weights = NULL;
double* prices = NULL;
int weights_length = 0;

// Structure to store partition
typedef struct Partition {
    double** subsets;
    int* subset_sizes;
    int num_subsets;
    struct Partition* next;  // For linked list implementation
} Partition;

// Structure to store the result
typedef struct {
    double price;
    int num_subsets;
    double** subsets;
    int* subset_sizes;
} OptimizationResult;

// Function to free allocated memory
void cleanup() {
    free(weights);
    free(prices);
    weights = NULL;
    prices = NULL;
}

// Function to set new tariffs
void set_new_tarif(double* new_weights, double* new_prices, int length) {
    cleanup();
    
    weights_length = length;
    weights = (double*)malloc(length * sizeof(double));
    prices = (double*)malloc(length * sizeof(double));
    
    if (weights == NULL || prices == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    memcpy(weights, new_weights, length * sizeof(double));
    memcpy(prices, new_prices, length * sizeof(double));
}

// Binary search implementation
int binary_search_right(double value) {
    int left = 0;
    int right = weights_length;
    
    while (left < right) {
        int mid = (left + right) / 2;
        if (weights[mid] <= value)
            left = mid + 1;
        else
            right = mid;
    }
    return left;
}

// Tarif par masse implementation
double tarif_par_masse(double masse) {
    if (masse <= weights[weights_length - 1]) {
        return prices[binary_search_right(masse) - 1];
    } else {
        return prices[weights_length - 1];
    }
}

// Helper function to calculate sum of a subset
double sum_subset(double* subset, int size) {
    double sum = 0;
    for (int i = 0; i < size; i++) {
        sum += subset[i];
    }
    return sum;
}

// Function to create a deep copy of a partition
Partition* copy_partition(Partition* orig) {
    if (!orig) return NULL;
    
    Partition* copy = (Partition*)malloc(sizeof(Partition));
    copy->num_subsets = orig->num_subsets;
    copy->subsets = (double**)malloc(orig->num_subsets * sizeof(double*));
    copy->subset_sizes = (int*)malloc(orig->num_subsets * sizeof(int));
    copy->next = NULL;
    
    for (int i = 0; i < orig->num_subsets; i++) {
        copy->subset_sizes[i] = orig->subset_sizes[i];
        copy->subsets[i] = (double*)malloc(copy->subset_sizes[i] * sizeof(double));
        memcpy(copy->subsets[i], orig->subsets[i], copy->subset_sizes[i] * sizeof(double));
    }
    
    return copy;
}

// Function to free a partition
void free_partition(Partition* p) {
    if (!p) return;
    
    for (int i = 0; i < p->num_subsets; i++) {
        free(p->subsets[i]);
    }
    free(p->subsets);
    free(p->subset_sizes);
    free(p);
}

// Function to add element to existing subset
Partition* add_to_subset(Partition* orig, int subset_idx, double element) {
    Partition* new_part = copy_partition(orig);
    if (!new_part) return NULL;
    
    // Reallocate the target subset
    double* new_subset = (double*)malloc((new_part->subset_sizes[subset_idx] + 1) * sizeof(double));
    memcpy(new_subset, new_part->subsets[subset_idx], new_part->subset_sizes[subset_idx] * sizeof(double));
    new_subset[new_part->subset_sizes[subset_idx]] = element;
    
    free(new_part->subsets[subset_idx]);
    new_part->subsets[subset_idx] = new_subset;
    new_part->subset_sizes[subset_idx]++;
    
    return new_part;
}

// Function to add new subset with single element
Partition* add_new_subset(Partition* orig, double element) {
    Partition* new_part = (Partition*)malloc(sizeof(Partition));
    if (!orig) {
        // Create first partition
        new_part->num_subsets = 1;
        new_part->subsets = (double**)malloc(sizeof(double*));
        new_part->subset_sizes = (int*)malloc(sizeof(int));
        new_part->subsets[0] = (double*)malloc(sizeof(double));
        new_part->subsets[0][0] = element;
        new_part->subset_sizes[0] = 1;
        new_part->next = NULL;
        return new_part;
    }
    
    new_part->num_subsets = orig->num_subsets + 1;
    new_part->subsets = (double**)malloc(new_part->num_subsets * sizeof(double*));
    new_part->subset_sizes = (int*)malloc(new_part->num_subsets * sizeof(int));
    
    // Copy existing subsets
    for (int i = 0; i < orig->num_subsets; i++) {
        new_part->subset_sizes[i] = orig->subset_sizes[i];
        new_part->subsets[i] = (double*)malloc(orig->subset_sizes[i] * sizeof(double));
        memcpy(new_part->subsets[i], orig->subsets[i], orig->subset_sizes[i] * sizeof(double));
    }
    
    // Add new subset with the element
    new_part->subsets[new_part->num_subsets - 1] = (double*)malloc(sizeof(double));
    new_part->subsets[new_part->num_subsets - 1][0] = element;
    new_part->subset_sizes[new_part->num_subsets - 1] = 1;
    new_part->next = NULL;
    
    return new_part;
}

// Recursive function to generate all partitions
Partition* generate_partitions(double* elements, int size, int start_idx) {
    if (start_idx >= size) {
        return NULL;
    }
    
    if (start_idx == size - 1) {
        // Base case: single element partition
        return add_new_subset(NULL, elements[start_idx]);
    }
    
    // Get partitions of remaining elements
    Partition* rest_parts = generate_partitions(elements, size, start_idx + 1);
    if (!rest_parts) {
        return add_new_subset(NULL, elements[start_idx]);
    }
    
    Partition* head = NULL;
    Partition* current = NULL;
    
    // For each existing partition
    Partition* rest_current = rest_parts;
    while (rest_current) {
        // Add to each existing subset
        for (int i = 0; i < rest_current->num_subsets; i++) {
            Partition* new_part = add_to_subset(rest_current, i, elements[start_idx]);
            if (new_part) {
                if (!head) {
                    head = new_part;
                    current = head;
                } else {
                    current->next = new_part;
                    current = new_part;
                }
            }
        }
        
        // Add as new subset
        Partition* new_part = add_new_subset(rest_current, elements[start_idx]);
        if (new_part) {
            if (!head) {
                head = new_part;
                current = head;
            } else {
                current->next = new_part;
                current = new_part;
            }
        }
        
        rest_current = rest_current->next;
    }
    
    // Free the rest_parts
    while (rest_parts) {
        Partition* temp = rest_parts;
        rest_parts = rest_parts->next;
        free_partition(temp);
    }
    
    return head;
}

// Function to cleanup the result
void cleanup_result(OptimizationResult* result) {
    if (result) {
        for (int i = 0; i < result->num_subsets; i++) {
            free(result->subsets[i]);
        }
        free(result->subsets);
        free(result->subset_sizes);
        free(result);
    }
}

// Main optimization function
OptimizationResult* find_best_config(double* elements, int elements_size) {
    if (elements_size == 0) {
        OptimizationResult* empty_result = (OptimizationResult*)malloc(sizeof(OptimizationResult));
        empty_result->price = 0;
        empty_result->num_subsets = 0;
        empty_result->subsets = NULL;
        empty_result->subset_sizes = NULL;
        return empty_result;
    }
    
    OptimizationResult* result = (OptimizationResult*)malloc(sizeof(OptimizationResult));
    result->price = DBL_MAX;
    result->num_subsets = 0;
    result->subsets = NULL;
    result->subset_sizes = NULL;
    
    // Generate all possible partitions
    Partition* all_partitions = generate_partitions(elements, elements_size, 0);
    
    // Find the best partition
    Partition* current = all_partitions;
    while (current) {
        double current_price = 0;
        for (int i = 0; i < current->num_subsets; i++) {
            current_price += tarif_par_masse(sum_subset(current->subsets[i], current->subset_sizes[i]));
        }
        
        if (current_price < result->price) {
            // Free previous best result
            if (result->subsets) {
                for (int i = 0; i < result->num_subsets; i++) {
                    free(result->subsets[i]);
                }
                free(result->subsets);
                free(result->subset_sizes);
            }
            
            // Copy current partition to result
            result->price = current_price;
            result->num_subsets = current->num_subsets;
            result->subsets = (double**)malloc(current->num_subsets * sizeof(double*));
            result->subset_sizes = (int*)malloc(current->num_subsets * sizeof(int));
            
            for (int i = 0; i < current->num_subsets; i++) {
                result->subset_sizes[i] = current->subset_sizes[i];
                result->subsets[i] = (double*)malloc(current->subset_sizes[i] * sizeof(double));
                memcpy(result->subsets[i], current->subsets[i], current->subset_sizes[i] * sizeof(double));
            }
        }
        
        current = current->next;
    }
    
    // Free all partitions
    while (all_partitions) {
        Partition* temp = all_partitions;
        all_partitions = all_partitions->next;
        free_partition(temp);
    }
    
    return result;
}