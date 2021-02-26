import matplotlib.pyplot as plt
import pandas as pd
import pytask
import seaborn as sns

PLOT_ARGS = {"markersize": 4, "alpha": 0.6}

from src.config import BLD


def plot_payout(data_with_negative_payout, data_total_payout, produces):

    sns.set_theme()
    # Draw a heatmap with the numeric values in each cell
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 5), sharex=True)
    fig.suptitle("Payout of swap contract")

    # convert to long-form
    data_with_negative_payout = data_with_negative_payout.rename(
        columns={
            "leverage": "Leverage factor",
            "USD_asset_allocation": "Share of assets invested in USD",
        }
    )
    data_with_negative_payout_pivot = data_with_negative_payout.pivot(
        "Leverage factor", "Share of assets invested in USD", "negative_payout"
    )

    sns.heatmap(
        data_with_negative_payout_pivot,
        ax=ax1,
        fmt=".1%",
        vmin=0,
        vmax=0.10,
        cmap="Reds",
    )

    # convert to long-form
    data_total_payout = data_total_payout.rename(
        columns={
            "leverage": "Leverage factor",
            "USD_asset_allocation": "Share of assets invested in USD",
        }
    )
    data_total_payout_pivot = data_total_payout.pivot(
        "Leverage factor", "Share of assets invested in USD", "total_payout"
    )
    sns.heatmap(data_total_payout_pivot, ax=ax2, fmt=".1%", cmap="Greens")

    # sns.kdeplot(data = negative_payout_share_long, ax=ax,  x="Leverage
    # factor", y="Share of assets invested in USD", fill=True)  #fmt=".1%",
    #  vmin=0, vmax=0.05, cmap="Reds")

    # format
    # for t in ax.texts: t.set_text(t.get_text() + " %")

    # save result to folder
    fig.savefig(produces)


def _merge_on_metadata(data, metadata):
    merged_dataset = data.merge(
        metadata,
        left_index=True,
        right_index=True,
        validate="one_to_one",
        indicator=True,
    )
    assert not (
        merged_dataset["_merge"] != "both"
    ).any(), "Rows can not be merged/ Metadata fraudulent"
    merged_dataset.drop(columns=["_merge"], inplace=True)
    return merged_dataset


def _aggregate_payout(data):
    data["total_payout"] = data["EURlong payout in EURO"].add(
        data["EURshort payout in EURO"]
    )
    data_total_payout = data.groupby("swap_config_id")[["total_payout"]].mean()
    return data_total_payout


def get_data_aggregated_payout(data, metadata):
    data_total_payout = _aggregate_payout(data)
    data_total_payout = _merge_on_metadata(data_total_payout, metadata)
    return data_total_payout


def _aggregate_data_with_negative_payout(data):
    data["negative_payout"] = (
        data[["EURlong payout in EURO", "EURshort payout in EURO"]] < 0
    ).any(axis="columns")
    data_with_negative_payout = data.groupby("swap_config_id")[
        ["negative_payout"]
    ].mean()
    return data_with_negative_payout


def get_data_with_negative_payout(data, metadata):
    data_with_negative_payout = _aggregate_data_with_negative_payout(data)
    data_with_negative_payout = _merge_on_metadata(data_with_negative_payout, metadata)
    return data_with_negative_payout


specifications = (
    (
        BLD / "simulated_payout" / f"simulated_payout_{simulation_name}.pickle",
        BLD / "metadata" / f"metadata_payout_{simulation_name}.pickle",
        BLD / "figures" / f"payout_{simulation_name}.png",
    )
    for simulation_name in ["historical", "bootstrapped"]
)


@pytask.mark.parametrize(
    "data_path, metadata_path, produces",
    specifications,
)
def task_swap_payout_analysis(data_path, metadata_path, produces):

    # load files
    data = pd.read_pickle(data_path)
    metadata = pd.read_pickle(metadata_path)

    # aggregate data
    data_with_negative_payout = get_data_with_negative_payout(data, metadata)
    data_total_payout = get_data_aggregated_payout(data, metadata)

    # plot payout
    plot_payout(data_with_negative_payout, data_total_payout, produces)

    # return data_with_negative_payout, data_total_payout


if __name__ == "__main__":
    simulation_name = "historical"
    data_path = BLD / "simulated_payout" / f"simulated_payout_{simulation_name}.pickle"
    metadata_path = BLD / "metadata" / f"metadata_payout_{simulation_name}.pickle"
    produces = BLD / "figures" / f"payout_{simulation_name}.png"

    data_with_negative_payout, data_total_payout = task_swap_payout_analysis(
        data_path, metadata_path, produces
    )
