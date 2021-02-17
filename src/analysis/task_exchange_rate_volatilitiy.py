import pickle
import json
import pytask
import pandas as pd
import numpy as np
from datetime import datetime
from src.config import BLD
from src.config import SRC

"""
def _yearslater(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return pd.Timestamp(year = from_date.year + years, month = from_date.month,  day = from_date.day)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return pd.Timestamp(year = from_date.year + years, month = 3,  day = 1)
"""

def generate_historical_one_year_returns(data, config):
    # initiate empty container
    simulated_historical_data = dict()
    trading_days = config["trading_days"]
    savings_period_years = config["savings_period_years"]
    data.dropna(axis = 'index', inplace=True)

    for i_start in range(len(data) - trading_days):
        i_end = i_start + trading_days
        simulated_historical_data[data.index[i_start]] = data.iloc[i_start: i_end]['log_return'].to_numpy().reshape((trading_days,1))

    return simulated_historical_data

@pytask.mark.depends_on(
    {
        "swap_config": SRC / "model_specs" / "currency_swap.json",
        "raw_data": BLD / "historical_data" / "raw_data.pickle"
    }
)
@pytask.mark.produces(BLD / "data" / "simulated_historical.pickle")

def task_simulated_sample(depends_on, produces):
    
    # Load locations after each round
    with open(depends_on["raw_data"], "rb") as f:
        raw_data = pickle.load(f)

    swap_config = json.loads(depends_on["swap_config"].read_text(encoding="utf-8"))
    historic_1_year = generate_historical_one_year_returns(raw_data, swap_config)

    # Store dictionary with locations once
    with open(produces, "wb") as out_file:
        pickle.dump(historic_1_year, out_file)


if __name__ == "__main__":
    # Evaluate production functions.
    depends_on =  {
        "swap_config": SRC / "model_specs" / "currency_swap.json",
        "raw_data": BLD / "historical_data" / "raw_data.pickle"
    }
    produces = BLD / "data" / "simulated_historical.pickle"
    task_simulated_sample(depends_on, produces)
