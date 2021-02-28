import pickle

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pytask
import seaborn as sns

from src.config import BLD
from src.simulation_analysis.utility import get_total_exchange_rate_change

PLOT_ARGS = {"markersize": 4, "alpha": 0.6}


def plot_total_change(data, path):
    """Plot the final exchange rate resulting from 1 year exchange rate
    movements

    Args:
        data (pd.DataFrame): Pandas DataFrame cumulated exchange rate movements.
        path (string): path of output file.
    """

    # set up multiple graphs
    fig, ax = plt.subplots()
    fig.suptitle("EURO/USD exchange rate")

    data = data.to_frame(name="Final exchange rate")

    # plot EURO/USD price
    ax.tick_params(labelbottom="off", labelleft="off")
    ax.set_facecolor("azure")
    sns.kdeplot(data=data, x="Final exchange rate", ax=ax)

    # set limits
    ax.set(xlim=(-0.4, 0.4))
    ax.set(ylim=(0, 4))

    # format labels
    xlabels = [i / 10 for i in range(-4, 5)]
    ax.xaxis.set_major_locator(mticker.FixedLocator(xlabels))
    ax.set_xticklabels([f"{x:,.2%}" for x in xlabels])  # format y axis

    # ax.set_xlabel('')  # remove x label

    # save result to folder
    fig.savefig(path)


specifications = (
    (
        BLD / "simulated_data" / f"simulated_data_{simulation_name}.pickle",
        BLD / "figures" / f"euro_usd_{simulation_name}.png",
    )
    for simulation_name in ["historical", "bootstrapped"]
)


@pytask.mark.parametrize("depends_on, produces", specifications)
def task_final_exchange_rate(depends_on, produces):
    with open(depends_on, "rb") as f:
        raw_data = pickle.load(f)
    total_change = get_total_exchange_rate_change(raw_data)
    plot_total_change(total_change, produces)


if __name__ == "__main__":
    # Evaluate production functions.
    simulation_name = "historical"
    depends_on = BLD / "simulated_data" / f"simulated_data_{simulation_name}.pickle"
    produces = BLD / "figures" / f"euro_usd_{simulation_name}.png"
    task_final_exchange_rate(depends_on, produces)
