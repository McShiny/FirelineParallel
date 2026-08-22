import csv
import hashlib

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

def check_group(group):
    for i in range(len(group) - 1):
        for elem in MUST_MATCH_FIELDS:
            if group[i][elem] != group[i + 1][elem]:
                return False
    
    return True

def image_path_row(row, kind):
    return f"output/{row["prefix"]}_{kind}.png"

def hash_file(path):
    hasher = hashlib.sha256()

    with open(path, "rb") as file:

        while chunk := file.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()

def check_kind(hashes):
    for i in range(len(hashes) - 1):
        if hashes[i] != hashes[i + 1]:
            return False

    return True

def compare_group_images(group):
    terrain = []
    peak = []
    final = []

    for i in range(len(group)):
        terrain.append(hash_file(image_path_row(group[i], "terrain")))
        peak.append(hash_file(image_path_row(group[i], "peak")))
        final.append(hash_file(image_path_row(group[i], "final")))

    return check_kind(terrain) and check_kind(peak) and check_kind(final)

groups = read_csv("benchmarks/output_validation_real.csv")

print("Testing Data")
print()
success = 0
incorrect = 0
incorrect_num = []
fail = 0
fail_num = []
for i in range(len(groups)):
    try:
        if check_group(groups[i]) and compare_group_images(groups[i]):
            success += 1
        else:
            incorrect += 1
            incorrect_num.append(i)
    except Exception:
        print("Error testing group:", i)
        fail_num.append(i)
        fail += 1

print("Finished Testing")
print("Tested:", success + fail + incorrect, "configurations")
print(success, "Succeded")
print(incorrect, "Incorrect")
print(*incorrect_num)
print(fail, "Failed")
print(*fail_num)


