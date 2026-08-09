import subprocess
import csv
import itertools
import argparse
import platform
import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class fireData:
    rows : int
    columns : int
    seed : int
    mode : str
    landscape : str
    cutoff : int
    max_steps : int
    tolerance : float
    max_steps = 5000
    tolerance = 0.05

