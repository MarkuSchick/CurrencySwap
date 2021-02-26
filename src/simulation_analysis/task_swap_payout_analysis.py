
import pickle
import pandas as pd
import pytask

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pytask
import seaborn as sns

PLOT_ARGS = {"markersize": 4, "alpha": 0.6}

from src.config import BLD


def plot_data_with_negative_payoff(negative_payoffs_share_long, path):

    sns.set_theme()


    # Load the example flights dataset and convert to long-form
    negative_payoffs_share_long = negative_payoffs_share_long.rename(columns={"leverage": "Leverage factor", "USD_asset_allocation": "Share of assets invested in USD"})
    negative_payoffs_share = negative_payoffs_share_long.pivot("Leverage factor", "Share of assets invested in USD", "negative_payoff")

    # Draw a heatmap with the numeric values in each cell
    fig, ax = plt.subplots(figsize=(9, 6))

    fig.suptitle("Share of historic with reserves < payoff")
    sns.heatmap(negative_payoffs_share, ax=ax, fmt=".1%", vmin=0, vmax=0.05, cmap="Reds")

    # format
    for t in ax.texts: t.set_text(t.get_text() + " %")

    # save result to folder
    fig.savefig(path)

def _aggregate_data_with_negative_payoff(data):
    data['negative_payoff'] = (data[['EURlong payout','EURshort payout']] < 0).any(axis = 'columns')
    data_with_negative_payoff = data.groupby('swap_config_id')[['negative_payoff']].mean()
    return data_with_negative_payoff

def _merge_on_metadata(data, metadata):
    merged_dataset = data.merge(metadata, left_index =True, right_index=True, validate="one_to_one", indicator=True)
    assert not (merged_dataset["_merge"] != "both").any(), "Rows can not be merged/ Metadata fraudulent"
    merged_dataset.drop(columns = ["_merge"], inplace=True)
    return merged_dataset

def get_data_with_negative_payoff(data, metadata):
    data_with_negative_payoff = _aggregate_data_with_negative_payoff(data)
    data_with_negative_payoff = _merge_on_metadata(data_with_negative_payoff, metadata)
    return data_with_negative_payoff

specifications = (
    (
        BLD / "simulated_payout" / f"simulated_payout_{simulation_name}.pickle",
        BLD / "metadata" / f"metadata_payout_{simulation_name}.pickle",
        BLD / "figures" / f"payout_{simulation_name}.png"
    )
    for simulation_name in ["historical", "bootstrapped"]
)
@pytask.mark.parametrize(
    "data_path, metadata_path, produces", specifications,
)
def task_swap_payout_analysis(data_path, metadata_path, produces):

    # load files
    data = pd.read_pickle(data_path)
    metadata = pd.read_pickle(metadata_path)

    data_with_negative_payoff = get_data_with_negative_payoff(data, metadata)
    plot_data_with_negative_payoff(data_with_negative_payoff, produces)


if __name__ == "__main__":
    simulation_name = "historical"
    data_path = BLD / "simulated_payout" / f"simulated_payout_{simulation_name}.pickle"
    metadata_path = BLD / "metadata" / f"metadata_payout_{simulation_name}.pickle"
    produces = BLD / "figures" / f"payout_{simulation_name}.png"

    task_swap_payout_analysis(data_path, metadata_path, produces)
