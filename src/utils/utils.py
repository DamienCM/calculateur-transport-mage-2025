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
    return int(n < 1) or k * partitions_count(n - 1, k) + partitions_count(n - 1, k + 1)


weights = []
prices = []


def set_new_tarif(new_weights, new_prices, max_weight):
    global weights, prices
    for i in range(len(new_weights)):
        if new_weights[i] > max_weight:
            new_prices[i] = float("inf")
    weights = new_weights
    prices = new_prices


@lru_cache(maxsize=None)
def tarif_par_masse(masse):
    print(f'[INFO] weights = {weights}')
    print(f'[INFO] prices = {prices}')
    if masse <= weights[-1]:
        price = prices[np.searchsorted(weights, masse, side="right")] 
        print(f'[INFO] Calculating tarif for masse {masse} kg, price = {price} euros')
        return price
    else:
        price = prices[-1]
        print(f'[WARNING] Calculating tarif for masse {masse} kg, price = {price} euros')
        return price


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
    rest_partitions = find_best_config(rest, i + 1)
    all_partitions = []
    counter = 0
    if i == 0:
        best_price = float("inf")
        best_config = []
    for partition in rest_partitions:
        # Ajouter 'first' à chaque sous-ensemble existant
        for j in range(len(partition)):
            new_partition = (
                partition[:j] + [partition[j] + [first]] + partition[j + 1 :]
            )
            if i == 0:
                counter += 1
                # print(f"{new_partition=}")
                mass = [sum(subset) for subset in new_partition]
                price = sum([tarif_par_masse(masse) for masse in mass])
                if price < best_price:
                    best_price = price
                    best_config = new_partition
                continue
            all_partitions.append(new_partition)
        # Ajouter 'first' comme nouveau sous-ensemble
        new_partition = [[first]] + partition
        if i == 0:
            # print(f"{new_partition=}")
            counter += 1
            mass = [sum(subset) for subset in new_partition]
            price = sum([tarif_par_masse(masse) for masse in mass])
            if price < best_price:
                best_price = price
                best_config = new_partition
        all_partitions.append(new_partition)
    if i == 0:
        print(f"counter={counter}")
        return best_price, best_config
    return all_partitions


def read_csv_file_with_headers(
    file_path, sep=",", header_sep=":", comment_symbols=["#", "//"],
    col_types = None, list_in_header = False
):
    """
    File format example:
        DATE : 2025         <-- Header
        AUTHOR : DCM        <-- Header with header sep :
        TAX % : 25          <-- Header
        PRICE, KG           <-- Columns label
        1, 5                <-- csv with sep ,
        2, 8                <-- csv

    """

    try:
        header = {}
        columns_labels = []
        csv = {}
        with open(file_path) as f:
            # Ignorer les deux premières lignes
            all_file_lines = f.readlines()
            # trigger
            in_header = True
            # trigger
            in_col_label_line = True

            # For each line in the file
            for line_index, line in enumerate(all_file_lines):

                # if line starts with comment go to next line
                skip_line = False
                for comment_symbol in comment_symbols:
                    if line.startswith(comment_symbol):
                        skip_line = True
                if skip_line: 
                    continue

                # Blank line : continue
                if line.strip() == "":
                    continue
                
                # if in header line should be like this  "key : value"
                if header_sep in line and in_header:
                    line_splitted = line.strip().lower().split(header_sep)
                    if len(line_splitted) != 2:
                        raise SyntaxError(
                            f"[ERROR Invalid csv header syntax at line {line_index} in file {file_path}, format should be 'key : value'"
                        )
                    else:
                        key, value = line_splitted
                        key = key.lower().strip()
                        if list_in_header and sep in value:
                            value = value.split(sep)
                            for v in value :
                                v = v.strip().lower()
                        else:
                            value = value.lower().strip()
                        header[key] = value
                # not in header
                else:
                    in_header = False
                    if sep in line:
                        line_splitted = line.strip().lower().split(sep)
                        for col_index, cell in enumerate(line_splitted):
                            cell = cell.strip().lower()
                            if in_col_label_line:
                                columns_labels.append(cell)
                                csv[cell] = []
                            else:
                                try:
                                    if col_types is not None:
                                        csv[columns_labels[col_index]].append(col_types[col_index](cell))
                                    else :
                                        csv[columns_labels[col_index]].append(cell)

                                except Exception as e:
                                    print(
                                        f"[ERROR] Could not read file {file_path} at line:{line_index+1}, column:{col_index}. inconsistent data"
                                    )
                                    raise SyntaxError(
                                        f"[ERROR] Could not read file {file_path} at line:{line_index+1}, column:{col_index}. inconsistent data"
                                    )
                                except ValueError as e:
                                    print(f'[ERROR] Could not convert cell value ({cell}) to {col_types[col_index]} ')
                                    raise ValueError(f'[ERROR] Could not convert cell value ({cell}) to {col_types[col_index]} ')
                        in_col_label_line = False
                    else:
                        continue
            return header, columns_labels, csv

    except FileNotFoundError as e:
        print(f"[ERROR] Price file not found \n{e}")
        raise e
    except Exception as e:
        print(f"[ERROR] Unhandeled error during price file reading \n{e}")
