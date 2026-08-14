import csv

MUST_MATCH_FIELDS = ["timesteps", "converged", "final_burning_cells", "cells_burned",
                     "max_peak_temp", "max_final_change"]

integers = ["rows", "columns", "seed", "timesteps", "final_burning_cells",
            "cells_burned", "rep", "cutoff", "max_steps"]
floats = ["max_peak_temp",  "max_final_change", "sim_time", "tolerance"]
strings = [ "mode", "landscape", "initial_source", "prefix", "warning", "kind"]
booleans = ["converged"]

def find_group(row, output):

    if len(output) == 0:
        output.append(list())
        output[0].append(row)
        return
    
    found = False
    for i in range(len(output)):
        if row["kind"] == "serial":
            if output[i][0]["kind"] == "serial":
                if row["prefix"] == output[i][0]["prefix"]:
                    output[i].append(row)
                    found = True
            elif row["prefix"] == output[i][0]["prefix"][:-2] + output[i][0]["prefix"][-1]:
                output[i].append(row)
                found = True
        elif output[i][0]["kind"] == "serial":
            if row["prefix"][:-2] + row["prefix"][-1] == output[i][0]["prefix"]:
                output[i].append(row)
                found = True
        elif row["prefix"][:-2] + row["prefix"][-1] == output[i][0]["prefix"][:-2] + output[i][0]["prefix"][-1]:
            output[i].append(row)
            found = True

    if not found:
        output.append(list())
        output[-1].append(row)

def read_csv(path):
    output = []
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
            find_group(converted_row, output)
        
        return output

