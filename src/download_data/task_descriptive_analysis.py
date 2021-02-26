import pickle

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pytask
import seaborn as sns

from src.config import BLD

PLOT_ARGS = {"markersize": 4, "alpha": 0.6}


def plot_historical_timeseries(euro_usd_pd, path):
    """Plot the historical EURO / USD exchange rate and percentage returns

    Args:
        euro_usd_pd (pd.DataFrame): daily EURO / USD data (must include price,
                                     pct_change and date as index).
        path (string): path to output graph.
    """

    # load data to dataframe
    euro_usd_pd = euro_usd_pd.rename(columns={"price": "Price", "pct_change": "Return"})
    euro_usd_pd["date"] = euro_usd_pd.index

    # set up multiple graphs
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 5), sharex=True)
    fig.suptitle("EURO/USD exchange rate")

    # plot EURO/USD price
    ax1.tick_params(labelbottom="off", labelleft="off")
    ax1.set_facecolor("azure")
    sns.lineplot(
        ax=ax1,
        x="date",
        y="Price",
        data=euro_usd_pd,
    )
    ax1.set_xlabel("")  # remove x label

    # plot EURO/USD (percentage) returns
    ax2.tick_params(labelbottom="off", labelleft="off")
    ax2.set_facecolor("azure")
    ax2.set(ylim=(-0.04, 0.04))

    ylabels = ax2.get_yticks().tolist()
    ax2.yaxis.set_major_locator(mticker.FixedLocator(ylabels))
    ax2.set_yticklabels([f"{x:,.2%}" for x in ylabels])  # format y axis

    sns.lineplot(
        ax=ax2,
        x="date",
        y="Return",
        data=euro_usd_pd,
    )

    ax2.set_xlabel("")  # remove x label

    # save result to folder
    fig.savefig(path)


@pytask.mark.depends_on(BLD / "historical_data" / "raw_data.pickle")
@pytask.mark.produces(BLD / "figures" / "euro_usd_timeseries.png")
def task_descriptive_analysis(depends_on, produces):

    # Load locations after each round
    with open(depends_on, "rb") as f:
        raw_data = pickle.load(f)

    plot_historical_timeseries(raw_data, produces)
