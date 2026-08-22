import subprocess
import csv
import itertools
from pathlib import Path
from dataclasses import dataclass, fields
import os
import re

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
    repetition : int = 1

    def __getitem__(self, index: int):
        field_name = fields(self)[index].name
        return getattr(self, field_name)

    def __len__(self):
        return len(fields(self)) 

# creates a unique id for each relevant scen
# structure: first 3 numbers rows, first 3 numbers columns, first letter mode, cutoff
# number(skipped for serial), 2 numbers removed max_steps, tolerance, 
# first letter landscape
def scenario_par_id(scenario):
    return f"{scenario[0] // 10}{scenario[1] //
        10}{scenario[2]}{scenario[3][0]}{scenario[4]}{scenario[5] // 100}{scenario[6]}{scenario[7][0]}"

def scenario_ser_id(scenario):
    return f"{scenario[0] // 10}{scenario[1] //
        10}{scenario[2]}{scenario[3][0]}{scenario[5] // 100}{scenario[6]}{scenario[7][0]}"

def format_scenario(scen, kind):
    output = []

    if kind.lower() == "serial":
        for i in range(len(scen)):
            if i == 4:
                output.append(f"output/{scenario_ser_id(scen)}")
                continue # Skip appending cutoff for serial program
            output.append(str(scen[i]))
    elif kind.lower() == "parallel":
        for i in range(len(scen)):
            if i == 4:
                output.append(f"output/{scenario_par_id(scen)}")
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

def run_program(name, args, extra_env=None):
    compile_project()

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    
    try:
        result = subprocess.run(["make", "run-" + name, 
                    f"ARGS={" ".join(list(map(lambda x: str(x), format_scenario(args, name))))}"], 
                    timeout=4800, capture_output=True, text=True, env=env)
        
        if result.returncode != 0:
            raise Exception("Running " + name + " program Failed\n" + result.stderr)
        else:
            return result.stdout
    except subprocess.TimeoutExpired as e:
        raise Exception("Timeout Error\n" + f"Program run: {e.cmd}\n" + f"Program timed out after {e.timeout} seconds.")

    
def process_output(output):

    integers = {"random seed": "seed", "timesteps completed": "timesteps", "final burning cells": "final_burning_cells", 
    "cells burned": "cells_burned", "repetition index": "repetition"}
    floats = {"maximum peak temperature": "max_peak_temp", "maximum change in final timestep": "max_final_change", 
    "core simulation time": "sim_time"}
    strings = {"mode": "mode", "landscape": "landscape", "initial source": "initial_source",
               "images written with prefix": "prefix", "warning": "warning"}
    booleans = {"converged": "converged"}
    values = output.split("\n")
    processed_output = dict()
    
    for elem in values:
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

def extract_core_count(extra_env):
    if not extra_env or "_JAVA_OPTIONS" not in extra_env:
        return os.cpu_count()
    match = re.search(r"ActiveProcessorCount=(\d+)", extra_env["_JAVA_OPTIONS"])
    return int(match.group(1)) if match else os.cpu_count()

def split_output_blocks(output):
    lines = output.split("\n")
    blocks, current = [], []
    started = False
    for line in lines:
        if line.startswith("Fireline parallel simulation") or line.startswith("Fireline serial simulation"):
            if started and current:
                blocks.append("\n".join(current))
            current = [line]
            started = True
        elif started:
            current.append(line)
    if started and current:
        blocks.append("\n".join(current))
    return blocks

def build_csv_row_full(scenario, kind, extra_env=None):

    def shorten_source(s):
        return s[s.find("("):s.find(")") + 1] + ", " + s.split(",")[2].split("=")[-1] + ", " + s[s.rfind("=") + 1:]
    
    raw = run_program(kind, scenario, extra_env)
    outputs = [process_output(b) for b in split_output_blocks(raw)]

    result_rows = []
    
    for output in outputs:
        output["kind"] = kind

        if kind.lower() == "serial":
            output["cutoff"] = None
        else:
            output["cutoff"] = scenario[4]

        output["prefix"] = output["prefix"].split("/")[-1]
        output["initial_source"] = shorten_source(output["initial_source"])

        output["max_steps"] = scenario[5]
        output["tolerance"] = scenario[6]
        if cores is not None:
            output["cores"] = extract_core_count(extra_env)

        if "warning" not in output:
            output["warning"] = None

        if "repetition" not in output:
            output["repetition"] = None

        result_rows.append(output)

    return result_rows

# CSV creating functions

def write_csv_full(rows):
    Path("benchmarks").mkdir(parents=True, exist_ok=True)
    with open("benchmarks/output_cutoffs_3.csv", mode="w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=list(rows[0]))

        writer.writeheader()

        writer.writerows(rows)

# data arrays
size = [[800, 800]]
seeds = [17]
modes = ["wildfire"]
cutoffs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
steps = [10000]
tolerances = [0.05]
landscapes = ["mixed"]

repetitions = 12

cores = [20]


# building scenarios
scenarios = []

for elem in itertools.product(size, seeds, modes, cutoffs, steps,
                              tolerances, landscapes):
    scenarios.append(Scenario(elem[0][0], elem[0][1], elem[1], elem[2], elem[3], elem[4],
                              elem[5], elem[6], repetitions))

# outputting runs of each scenario to csv
rows = []
printed_percents = []
success = 0
fail = 0

# creating list of dictionaries(csv lines)
print("Creating csv rows")
for i in range(len(scenarios)):
    for core in cores:
        extra_env = {"_JAVA_OPTIONS": f"-XX:ActiveProcessorCount={core}"}
        if (i * 100) // len(scenarios) not in printed_percents:
            print(f"Percent Complete: {(i * 100) // len(scenarios)}%")
            printed_percents.append((i * 100) // len(scenarios))
        try:
            rows.extend(build_csv_row_full(scenarios[i], "parallel", extra_env))
            success += 1
            #rows.extend(build_csv_row_full(scenarios[i], "serial", extra_env))
            #success += 1
        except Exception as e:
            print("Error")
            print(f"Run {i + 1}")
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

