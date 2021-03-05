"""
Generate graphs to show how the
payout of the swap contract changes
depending on

Data from both implemented methods is used:|
# historical (based on historical 1 year returns) |
# bootstrapped (stationary bootstrapped returns from historical sample) |

Bootstrapping is done with the recombinator package.
See: https://github.com/InvestmentSystems/recombinator


Further simulation function can be parsed as arguments to the iterator object
specifications.
"""
import matplotlib.pyplot as plt
import pandas as pd
import pytask
import seaborn as sns

PLOT_ARGS = {"markersize": 4, "alpha": 0.6}

from src.config import BLD
from src.simulation_analysis.utility import (
    _merge_many_to_one_metadata,
    _merge_one_to_one_metadata,
)


def _aggregate_runs_with_negative_payout(data):
    negative_payout_data = (
        (data[["EURlong payout in EURO", "EURshort payout in EURO"]] < 0)
        .any(axis="columns")
        .to_frame(name="negative_payout")
    )
    negative_payout_data_aggregated = negative_payout_data.groupby(
        "swap_config_id"
    ).mean()
    return negative_payout_data_aggregated


def _get_runs_with_negative_payout(data, metadata):
    _runs_with_negative_payout = _aggregate_runs_with_negative_payout(data)
    _runs_with_negative_payout_merged = _merge_one_to_one_metadata(
        _runs_with_negative_payout, metadata
    )
    assert not _runs_with_negative_payout_merged.empty, "Dataframe is empty"
    return _runs_with_negative_payout_merged


def plot_negative_payout(payout_data, payout_metadata, figure_path, simulation_name):
    """Plot share of runs with negative payout

    Args:
        payout_data (pd.DataFrame): dataset with payout data
        payout_metadata  (pd.DataFrame): dataset with metainformation about run
        (leverage, asset allocation)
        figure_path (str): output path
        simulation_name (str): Type of simulation (bootstrapp or historical)
    """
    runs_with_negative_payout = _get_runs_with_negative_payout(
        payout_data, payout_metadata
    )

    sns.set_theme()
    # Initialize graph
    fig, ax = plt.subplots()
    fig.suptitle("Share of runs with negative payout of any asset")

    # Plot ratio of runs with a negative payout
    plot_runs_with_negative_payout = runs_with_negative_payout.rename(
        columns={
            "leverage": "Leverage factor",
            "USD_asset_allocation": "Share of assets invested in USD",
        }
    )
    plot_runs_with_negative_payout_pivot = plot_runs_with_negative_payout.pivot(
        "Leverage factor", "Share of assets invested in USD", "negative_payout"
    )
    sns.heatmap(
        plot_runs_with_negative_payout_pivot,
        ax=ax,
        fmt=".1%",
        vmin=0,
        vmax=0.10,
        cmap="Reds",
    )
    fig.savefig(figure_path / f"{simulation_name}_negative_payout.png")


def _calculate_total_payout_EUR(data):
    total_payout = (
        data["EURlong payout in EURO"]
        .add(data["EURshort payout in EURO"])
        .to_frame(name="total_payout")
    )
    return total_payout


def _keep_columns_total_payout(payout_data):
    keep_payout_data = payout_data.query("leverage==2")[
        ["total_payout", "USD_asset_allocation"]
    ].reset_index(drop=True)
    return keep_payout_data


def _get_run_total_payout_EUR(data, metadata):
    total_payout_data = _calculate_total_payout_EUR(data)
    total_payout_data = _merge_many_to_one_metadata(total_payout_data, metadata)
    total_payout_aggregated = _keep_columns_total_payout(total_payout_data)
    assert not total_payout_aggregated.empty, "Dataframe is empty"
    return total_payout_aggregated


def plot_expected_payout_EUR(
    payout_data, payout_metadata, figure_path, simulation_name
):
    """Plot total (EURlong + EURshort) expected payout in EURO

    Args:
        payout_data (pd.DataFrame): dataset with payout data
        payout_metadata  (pd.DataFrame): dataset with metainformation about run
        (leverage, asset allocation)
        figure_path (str): output path
        simulation_name (str): Type of simulation (bootstrapp or historical)
    """
    runs_total_payout = _get_run_total_payout_EUR(payout_data, payout_metadata)

    sns.set_theme()
    # Initialize graph
    fig, ax = plt.subplots()
    fig.suptitle("Expected total payout in Euro")

    # Plot average payout
    plot_total_payout_data = runs_total_payout.rename(
        columns={
            "total_payout": "Total payout",
            "USD_asset_allocation": "Share of assets invested in USD",
        }
    )
    plt.xlim(0, 1)
    plt.ylim(1.5, 2.5)
    sns.kdeplot(
        data=plot_total_payout_data,
        ax=ax,
        x="Share of assets invested in USD",
        y="Total payout",
        fill=True,
    )
    fig.savefig(figure_path / f"{simulation_name}_expected_payout_EUR.png")


def _calculate_total_payout_USD(data):
    total_payout = (
        data["EURlong payout in USD"]
        .add(data["EURshort payout in USD"])
        .to_frame(name="total_payout")
    )
    return total_payout


def _get_run_total_payout_USD(data, metadata):
    total_payout_data = _calculate_total_payout_USD(data)
    total_payout_data = _merge_many_to_one_metadata(total_payout_data, metadata)
    total_payout_aggregated = _keep_columns_total_payout(total_payout_data)
    assert not total_payout_aggregated.empty, "Dataframe is empty"
    return total_payout_aggregated


def plot_expected_payout_USD(
    payout_data, payout_metadata, figure_path, simulation_name
):
    """Plot total (EURlong + EURshort) expected payout in USD

    Args:
        payout_data (pd.DataFrame): dataset with payout data
        payout_metadata  (pd.DataFrame): dataset with metainformation about run
        (leverage, asset allocation)
        figure_path (str): output path
        simulation_name (str): Type of simulation (bootstrapp or historical)
    """
    runs_total_payout = _get_run_total_payout_USD(payout_data, payout_metadata)
    sns.set_theme()
    # Initialize graph
    fig, ax = plt.subplots()
    fig.suptitle("Expected total payout in  USD")

    # Plot average payout
    plot_total_payout_data = runs_total_payout.rename(
        columns={
            "total_payout": "Total payout",
            "USD_asset_allocation": "Share of assets invested in USD",
        }
    )
    plt.xlim(0, 1)
    plt.ylim(1.5, 2.5)
    sns.kdeplot(
        data=plot_total_payout_data,
        ax=ax,
        x="Share of assets invested in USD",
        y="Total payout",
        fill=True,
    )
    fig.savefig(figure_path / f"{simulation_name}_expected_payout_USD.png")


def _aggregate_run_eurlong_payout(data):
    aggregated_eurlong_payout_data = (
        data[["EURlong payout in EURO"]].groupby("swap_config_id").mean()
    )
    return aggregated_eurlong_payout_data


def _get_run_eurlong_payout(data, metadata):
    run_eurlong_payout = _aggregate_run_eurlong_payout(data)
    run_eurlong_payout_merged = _merge_many_to_one_metadata(
        run_eurlong_payout, metadata
    )
    run_eurlong_payout_merged = run_eurlong_payout_merged[
        ["EURlong payout in EURO", "USD_asset_allocation"]
    ]
    assert not run_eurlong_payout_merged.empty, "Dataframe is empty"
    return run_eurlong_payout_merged


def plot_eurlong_payout(payout_data, payout_metadata, figure_path, simulation_name):
    """Plot the expected payout of the EURlong certificate

    Args:
        payout_data (pd.DataFrame): dataset with payout data
        payout_metadata  (pd.DataFrame): dataset with metainformation about run
        (leverage, asset allocation)
        figure_path (str): output path
        simulation_name (str): Type of simulation (bootstrapp or historical)
    """
    runs_eurlong_payout = _get_run_eurlong_payout(payout_data, payout_metadata)

    sns.set_theme()
    # Initialize graph
    fig, ax = plt.subplots()
    fig.suptitle("Eurlong payout depending on certificate payout of certificate")

    # Plot average payout
    plot_runs_eurlong_payout = runs_eurlong_payout.rename(
        columns={"USD_asset_allocation": "Share of assets invested in USD"}
    )
    plt.xlim(0, 1)
    sns.kdeplot(
        data=plot_runs_eurlong_payout,
        ax=ax,
        x="Share of assets invested in USD",
        y="EURlong payout in EURO",
        fill=True,
    )

    fig.savefig(figure_path / f"{simulation_name}_eurlong_payout.png")


def _aggregate_run_eurshort_payout(data):
    aggregated_eurshort_payout_data = (
        data[["EURshort payout in EURO"]].groupby("swap_config_id").mean()
    )
    return aggregated_eurshort_payout_data


def _get_run_eurshort_payout(data, metadata):
    run_eurshort_payout = _aggregate_run_eurshort_payout(data)
    run_eurshort_payout_merged = _merge_many_to_one_metadata(
        run_eurshort_payout, metadata
    )
    run_eurshort_payout_merged = run_eurshort_payout_merged[
        ["EURshort payout in EURO", "USD_asset_allocation"]
    ]
    assert not run_eurshort_payout_merged.empty, "Dataframe is empty"
    return run_eurshort_payout_merged


def plot_eurshort_payout(payout_data, payout_metadata, figure_path, simulation_name):
    """Plot the expected payout of the EURshort certificate

    Args:
        payout_data (pd.DataFrame): dataset with payout data
        payout_metadata  (pd.DataFrame): dataset with metainformation about run
        (leverage, asset allocation)
        figure_path (str): output path
        simulation_name (str): Type of simulation (bootstrapp or historical)
    """
    runs_eurshort_payout = _get_run_eurshort_payout(payout_data, payout_metadata)

    sns.set_theme()
    # Initialize graph
    fig, ax = plt.subplots()
    fig.suptitle("Eurshort payout depending on certificate payout of certificate")

    # Plot average payout
    plot_runs_eurshort_payout = runs_eurshort_payout.rename(
        columns={"USD_asset_allocation": "Share of assets invested in USD"}
    )
    plt.xlim(0, 1)
    sns.kdeplot(
        data=plot_runs_eurshort_payout,
        ax=ax,
        x="Share of assets invested in USD",
        y="EURshort payout in EURO",
        fill=True,
    )

    fig.savefig(figure_path / f"{simulation_name}_eurshort_payout.png")


specifications = (
    (
        BLD / "simulated_payout" / f"simulated_payout_{simulation_name}.pickle",
        BLD / "metadata" / f"metadata_payout_{simulation_name}.pickle",
        BLD / "figures",
        simulation_name,
    )
    for simulation_name in ["historical", "bootstrapped"]
)


@pytask.mark.parametrize(
    "data_path, metadata_path, figure_path, simulation_name",
    specifications,
)
def task_swap_payout_analysis(data_path, metadata_path, figure_path, simulation_name):

    # load files
    payout_data = pd.read_pickle(data_path)
    payout_metadata = pd.read_pickle(metadata_path)

    # plot negative payout
    plot_negative_payout(payout_data, payout_metadata, figure_path, simulation_name)

    # plot total payout (EUR)
    plot_expected_payout_EUR(payout_data, payout_metadata, figure_path, simulation_name)

    # plot total payout (USD)
    plot_expected_payout_USD(payout_data, payout_metadata, figure_path, simulation_name)

    # plot EURlong payout
    plot_eurlong_payout(payout_data, payout_metadata, figure_path, simulation_name)

    # plot EURshort payout
    plot_eurshort_payout(payout_data, payout_metadata, figure_path, simulation_name)


if __name__ == "__main__":
    simulation_name = "bootstrapped"
    data_path = BLD / "simulated_payout" / f"simulated_payout_{simulation_name}.pickle"
    metadata_path = BLD / "metadata" / f"metadata_payout_{simulation_name}.pickle"
    figure_path = BLD / "figures"

    task_swap_payout_analysis(data_path, metadata_path, figure_path, simulation_name)
