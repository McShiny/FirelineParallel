import subprocess
import csv
import itertools
import argparse
import platform
import os
from pathlib import Path
from dataclasses import dataclass, fields

@dataclass
class Scenario:
    rows : int
    columns : int
    seed : int
    mode : str
    cutoff : int = 5
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
    else:
        print("Compilation Succeeded")

num_rows = [500, 300]
num_cols = [500, 300]
seeds = [17, 21]
modes = ["diffusion", "wildfire"]
cutoffs = [4, 6]
steps = [5000]
tolerances = [0.05]
landscapes = ["mixed", "grass"]


scenarios = []

for elem in itertools.product(num_rows, num_cols, seeds, modes, cutoffs, steps,
                              tolerances, landscapes):
    scenarios.append(Scenario(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5],
                              elem[6], elem[7]))

compile_project()

