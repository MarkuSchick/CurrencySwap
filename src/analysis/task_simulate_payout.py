import json
import pickle

import numpy as np
import pytask

from src.config import BLD
from src.config import SRC
from src.model_code.swap_contract import payout_currency_swap


@pytask.mark.depends_on(
    {
        "sim_config": SRC / "model_specs" / "simulation_config.json",
        "data": BLD / "data" / f"simulated_data_historical.pickle",
    }
)
def task_simulate_payout(depends_on):
    with open(depends_on["data"], "rb") as f:
        raw_data = pickle.load(f)
    print("Hllo")


if __name__ == "__main__":
    # Evaluate production functions.
    depends_on = {
        "sim_config": SRC / "model_specs" / "simulation_config.json",
        "data": BLD / "data" / f"simulated_data_bootstrapped.pickle",
    }

    task_simulate_payout(depends_on)
