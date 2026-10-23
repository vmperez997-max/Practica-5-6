import argparse

from inf8239_u04.experiment import run_experiments

p = argparse.ArgumentParser()
p.add_argument(
    "--model",
    choices=["logistic", "tree", "all"],
    default="all",
    help="Compatibility flag: complete common comparison is always executed, preserving all model outputs.",
)
p.parse_args()
run_experiments()
