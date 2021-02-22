import pickle
from os import listdir
from os.path import isfile
from os.path import join

import pytask

from src.config import BLD


@pytask.mark.depends_on(BLD / "simulated_payout")
@pytask.mark.produces(BLD / "figures")
def task_swap_payout_analysis(depends_on, produces):

    simulate_payout = [
        f
        for f in listdir(depends_on)
        if isfile(join(depends_on, f)) and f.endswith(".pickle")
    ]

    for file_name in simulate_payout:

        # load files
        with open(depends_on / file_name, "rb") as f:
            raw_data = pickle.load(f)

        out_name = file_name.replace("simulated_payout", "simulated_payout").replace(
            ".pickle", ".png"
        )


if __name__ == "__main__":
    depends_on = BLD / "simulated_payout"
    produces = BLD / "figures"

    task_swap_payout_analysis(depends_on, produces)
