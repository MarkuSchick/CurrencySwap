import pickle
import json
import pytask
import pandas as pd
import numpy as np
from datetime import datetime
from src.config import BLD
from src.config import SRC

def _yearslater(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return pd.Timestamp(year = from_date.year + years, month = from_date.month,  day = from_date.day)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return pd.Timestamp(year = from_date.year + years, month = 2,  day = 28)


def generate_historical_one_year_returns(data, config):
    # initiate empty container
    simulated_historical_data = []

    # loop over dates
    for start_date in data.index[1:]:
        # fix end date 1 year in advance
        end_date = _yearslater(config["savings_period_years"], from_date=start_date)

        if end_date > datetime.today():
            break
        else:
            simulated_historical_data.append(data.loc[start_date:end_date]['log_return'].values)

    print("hello")
    data = np.concatenate(simulated_historical_data)
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
