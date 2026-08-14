import csv
import numpy as np
import matplotlib.pyplot as plt

MUST_MATCH_FIELDS = ["timesteps", "converged", "final_burning_cells", "cells_burned",
                     "max_peak_temp", "max_final_change"]

integers = ["rows", "columns", "seed", "timesteps", "final_burning_cells",
            "cells_burned", "rep", "cutoff", "max_steps"]
floats = ["max_peak_temp",  "max_final_change", "sim_time", "tolerance"]
strings = [ "mode", "landscape", "initial_source", "prefix", "warning", "kind"]
booleans = ["converged"]

def find_group(row, serial, parallel):

    if row["kind"] == "serial" and row["converged"]:
        serial.append(row)
    elif row["converged"]:
        parallel.append(row)

def read_csv(path):
    serial = []
    parallel = []

    with open(path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)

        header = next(reader)
        
        for row in reader:
            converted_row = dict()
            for i in range(len(row)):
                if header[i] in  integers:
                    if header[i] == "cutoff" and row[i] == "":
                        converted_row[header[i]] = None
                        continue
                    converted_row[header[i]] = int(row[i])    
                elif header[i] in floats:
                    converted_row[header[i]] = float(row[i])
                elif header[i] in strings:
                    if header[i] == "warning" and len(row[i]) < 1:
                        converted_row[header[i]] = None
                        continue
                    converted_row[header[i]] = row[i]
                else:
                    if row[i] == "True":
                        converted_row[header[i]] = True
                    else:
                        converted_row[header[i]] = False
            find_group(converted_row, serial, parallel)
        
        return np.array(serial), np.array(parallel)

def create_data_arrays(x_name, y_name, dict_data):
    x_data = []
    y_data = []

    if x_name == "size":
        for elem in dict_data:
            for key in elem:
                if key == y_name:
                    y_data.append(elem[key])
            
            x_data.append(elem["rows"] * elem["columns"])

        return x_data, y_data
    
    for elem in dict_data:
        for key in elem:
            if key == x_name:
                x_data.append(elem[key])
            elif key == y_name:
                y_data.append(elem[key])

    return x_data, y_data

def plot_data(x1, y1, x2, y2):
    plt.scatter(x1, y1, label="Serial")
    plt.scatter(x2, y2, label="Parallel")
    plt.show()

serial_dicts, parallel_dicts = read_csv("benchmarks/output.csv")

plot_data(*create_data_arrays("size", "sim_time", serial_dicts),
          *create_data_arrays("size", "sim_time", parallel_dicts))

