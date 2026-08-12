import subprocess
import csv
import itertools
from pathlib import Path
from dataclasses import dataclass, fields

@dataclass
class Scenario:
    rows : int
    columns : int
    seed : int
    mode : str
    cutoff : int = 0
    max_steps : int = 5000
    tolerance : float = 0.05
    landscape : str = "Mixed"

    def __getitem__(self, index: int):
        field_name = fields(self)[index].name
        return getattr(self, field_name)

    def __len__(self):
        return len(fields(self)) 

# creates a unique id for each relevant scen
# structure: first 3 numbers rows, first 3 numbers columns, first letter mode, cutoff
# number(skipped for serial), first letter landscape
def scenario_par_id(scenario):
    return f"{scenario[0] // 10}{scenario[1] //
        10}{scenario[2]}{scenario[3][0]}{scenario[4]}{scenario[7][0]}"

def scenario_ser_id(scenario):
    return f"{scenario[0] // 10}{scenario[1] //
        10}{scenario[2]}{scenario[3][0]}{scenario[7][0]}"

def format_scenario(scen, kind):
    output = []

    if kind.lower() == "serial":
        for i in range(len(scen)):
            if i == 4:
                output.append(f"output/serial/{scenario_ser_id(scen)}")
                continue # Skip appending cutoff for serial program
            output.append(str(scen[i]))
    elif kind.lower() == "parallel":
        for i in range(len(scen)):
            if i == 4:
                output.append(f"output/parallel/{scenario_par_id(scen)}")
                # no continue as cutoff is required
            output.append(str(scen[i]))
    else:
        raise Exception("not supported program type")

    return output

def compile_project():
    result = subprocess.run(["make", "compile"], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        raise Exception("Compilation Failed")

def run_program(name, args):
    compile_project()
    
    try:
        result = subprocess.run(["make", "run-" + name, 
                    f"ARGS={" ".join(list(map(lambda x: str(x), format_scenario(args, name))))}"], 
                    timeout=180, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception("Running " + name + " program Failed\n" + result.stderr)
        else:
            return result.stdout
    except subprocess.TimeoutExpired as e:
        raise Exception("Timeout Error\n" + f"Program run: {e.cmd}\n" + f"Program timed out after {e.timeout} seconds.")

    
def process_output(output):

    integers = {"random seed": "seed", "timesteps completed": "timesteps", "final burning cells": "final_burning_cells", 
    "cells burned": "cells_burned"}
    floats = {"maximum peak temperature": "max_peak_temp", "maximum change in final timestep": "max_final_change", 
    "core simulation time": "sim_time"}
    strings = {"mode": "mode", "landscape": "landscape", "initial source": "initial_source",
               "images written with prefix": "prefix", "warning": "warning"}
    booleans = {"converged": "converged"}
    values = output.split("\n")
    processed_output = dict()
    
    for elem in values[:len(values) - 1]:
        temp = elem.split(":")

        if len(temp) < 2:
            continue
        elif temp[0].lower() == "rows":
            processed_output["rows"] = int(temp[1].split(",")[0])
            processed_output["columns"] = int(temp[2].strip(" "))
        elif temp[0].lower() in integers:
            processed_output[integers[temp[0].lower()]] = int(temp[1].strip(" "))
        elif temp[0].lower() in floats:
            processed_output[floats[temp[0].lower()]] = float(temp[1].strip(" ms"))
        elif temp[0].lower() in booleans:
            if "yes" in temp[1]:
                value = True
            else:
                value = False
            processed_output[booleans[temp[0].lower()]] = value
        else:
            processed_output[strings[temp[0].lower()]] = temp[1].strip(" ")

    return processed_output

def build_csv_row_full(scenario, kind, repitition):

    def shorten_source(s):
        return s[s.find("("):s.find(")") + 1] + ", " + s.split(",")[2].split("=")[-1] + ", " + s[s.rfind("=") + 1:]

    output = process_output(run_program(kind, scenario))

    output["kind"] = kind
    output["rep"] = repitition

    if kind.lower() == "serial":
        output["cutoff"] = None
    else:
        output["cutoff"] = scenario[4]

    output["prefix"] = output["prefix"].split("/")[-1]
    output["initial_source"] = shorten_source(output["initial_source"])

    output["max_steps"] = scenario[5]
    output["tolerance"] = scenario[6]

    if "warning" not in output:
        output["warning"] = None

    return output

# CSV creating functions

def write_csv_full(rows):
    Path("benchmarks").mkdir(parents=True, exist_ok=True)
    with open("benchmarks/output.csv", mode="w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=list(rows[0]))

        writer.writeheader()

        writer.writerows(rows)

# data arrays
num_rows = [500, 300]
num_cols = [500, 300]
seeds = [17]
modes = ["wildfire"]
cutoffs = [6]
steps = [5000]
tolerances = [0.05]
landscapes = ["mixed"]


# building scenarios
scenarios = []

for elem in itertools.product(num_rows, num_cols, seeds, modes, cutoffs, steps,
                              tolerances, landscapes):
    scenarios.append(Scenario(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5],
                              elem[6], elem[7]))

# outputting runs of each scenario to csv
rows = []
repetitions = 2
printed_percents = []
success = 0
fail = 0

# creating list of dictionaries(csv lines)
print("Creating csv rows")
for i in range(len(scenarios)):
    if (i * 100) // len(scenarios) not in printed_percents:
        print(f"Percent Complete: {(i * 100) // len(scenarios)}%")
        printed_percents.append((i * 100) // len(scenarios))
    for j in range(repetitions):
        try:
            rows.append(build_csv_row_full(scenarios[i], "parallel", j))
            success += 1
            rows.append(build_csv_row_full(scenarios[i], "serial", j))
            success += 1
        except Exception as e:
            print("Error")
            print(f"Run {i * repetitions + j + 1}")
            print("Scenario:", *scenarios[i])
            print()
            print(e.args)
            fail += 1

print()
print("Creating rows finished")

# writing csv files
print()
print("Writing files")
write_csv_full(rows)

print()
print("Test Finished")
print(f"Tested {success + fail} configurations")
print(f"{success} sucessful runs")
print(f"{fail} failed runs")

