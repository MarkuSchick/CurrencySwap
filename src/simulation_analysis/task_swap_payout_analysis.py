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


def plot_negative_payout(runs_with_negative_payout, figure_path, simulation_name):
    """[summary]

    Args:
        runs_with_negative_payout (pd.Series): [description]
        simulation_name (str): [description]
        graph_path (string): [description]
    """

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


def plot_expected_payout_EUR(runs_total_payout, figure_path, simulation_name):
    """[summary]

    Args:
        runs_with_negative_payout (pd.Series): [description]
        graph_path (string): [description]
    """

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


def plot_expected_payout_USD(runs_total_payout, figure_path, simulation_name):
    """[summary]

    Args:
        runs_with_negative_payout (pd.Series): [description]
        graph_path (string): [description]
    """

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


def plot_eurlong_payout(runs_eurlong_payout, figure_path, simulation_name):
    """[summary]

    Args:
        runs_with_negative_payout (pd.Series): [description]
        graph_path (string): [description]
    """

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


def plot_eurshort_payout(runs_eurshort_payout, figure_path, simulation_name):
    """[summary]

    Args:
        runs_with_negative_payout (pd.Series): [description]
        graph_path (string): [description]
    """

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


def _merge_many_to_one_metadata(not_aggregated_data, metadata):
    merged_dataset = not_aggregated_data.merge(
        metadata,
        left_index=True,
        right_index=True,
        validate="many_to_one",
        indicator=True,
    )
    assert not (
        merged_dataset["_merge"] != "both"
    ).any(), "Rows can not be merged/ Metadata fraudulent"
    merged_dataset.drop(columns=["_merge"], inplace=True)
    return merged_dataset


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


def get_run_total_payout_EUR(data, metadata):
    """[summary]

    Args:
        data ([type]): [description]
        metadata ([type]): [description]

    Returns:
        [type]: [description]
    """
    total_payout_data = _calculate_total_payout_EUR(data)
    total_payout_data = _merge_many_to_one_metadata(total_payout_data, metadata)
    total_payout_aggregated = _keep_columns_total_payout(total_payout_data)
    assert not total_payout_aggregated.empty, "Dataframe is empty"
    return total_payout_aggregated


def _calculate_total_payout_USD(data):
    total_payout = (
        data["EURlong payout in USD"]
        .add(data["EURshort payout in USD"])
        .to_frame(name="total_payout")
    )
    return total_payout


def get_run_total_payout_USD(data, metadata):
    """[summary]

    Args:
        data ([type]): [description]
        metadata ([type]): [description]

    Returns:
        [type]: [description]
    """
    total_payout_data = _calculate_total_payout_USD(data)
    total_payout_data = _merge_many_to_one_metadata(total_payout_data, metadata)
    total_payout_aggregated = _keep_columns_total_payout(total_payout_data)
    assert not total_payout_aggregated.empty, "Dataframe is empty"
    return total_payout_aggregated


def _merge_one_to_one_metadata(aggregated_data, metadata):
    merged_dataset = aggregated_data.merge(
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


def get_runs_with_negative_payout(data, metadata):
    """[summary]

    Args:
        data (pd.DataFrame): dataframe with simulation data
        metadata (pd.DataFrame): dataframe with run configurations

    Returns:
        [type]: [description]
    """
    _runs_with_negative_payout = _aggregate_runs_with_negative_payout(data)
    _runs_with_negative_payout_merged = _merge_one_to_one_metadata(
        _runs_with_negative_payout, metadata
    )
    assert not _runs_with_negative_payout_merged.empty, "Dataframe is empty"
    return _runs_with_negative_payout_merged


def _aggregate_run_eurlong_payout(data):
    aggregated_eurlong_payout_data = (
        data[["EURlong payout in EURO"]].groupby("swap_config_id").mean()
    )
    return aggregated_eurlong_payout_data


def get_run_eurlong_payout(data, metadata):
    run_eurlong_payout = _aggregate_run_eurlong_payout(data)
    run_eurlong_payout_merged = _merge_many_to_one_metadata(
        run_eurlong_payout, metadata
    )
    run_eurlong_payout_merged = run_eurlong_payout_merged[
        ["EURlong payout in EURO", "USD_asset_allocation"]
    ]
    assert not run_eurlong_payout_merged.empty, "Dataframe is empty"
    return run_eurlong_payout_merged


def _aggregate_run_eurshort_payout(data):
    aggregated_eurshort_payout_data = (
        data[["EURshort payout in EURO"]].groupby("swap_config_id").mean()
    )
    return aggregated_eurshort_payout_data


def get_run_eurshort_payout(data, metadata):
    run_eurshort_payout = _aggregate_run_eurshort_payout(data)
    run_eurshort_payout_merged = _merge_many_to_one_metadata(
        run_eurshort_payout, metadata
    )
    run_eurshort_payout_merged = run_eurshort_payout_merged[
        ["EURshort payout in EURO", "USD_asset_allocation"]
    ]
    assert not run_eurshort_payout_merged.empty, "Dataframe is empty"
    return run_eurshort_payout_merged


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
    runs_with_negative_payout = get_runs_with_negative_payout(
        payout_data, payout_metadata
    )
    plot_negative_payout(runs_with_negative_payout, figure_path, simulation_name)

    # plot total payout (EUR)
    runs_total_payout_EUR = get_run_total_payout_EUR(payout_data, payout_metadata)
    plot_expected_payout_EUR(runs_total_payout_EUR, figure_path, simulation_name)

    # plot total payout (USD)
    runs_total_payout_USD = get_run_total_payout_USD(payout_data, payout_metadata)
    plot_expected_payout_USD(runs_total_payout_USD, figure_path, simulation_name)

    # plot EURO long payout
    runs_eurlong_payout = get_run_eurlong_payout(payout_data, payout_metadata)
    plot_eurlong_payout(runs_eurlong_payout, figure_path, simulation_name)

    # plot EURO short payout
    runs_eurshort_payout = get_run_eurshort_payout(payout_data, payout_metadata)
    plot_eurshort_payout(runs_eurshort_payout, figure_path, simulation_name)


if __name__ == "__main__":
    simulation_name = "bootstrapped"
    data_path = BLD / "simulated_payout" / f"simulated_payout_{simulation_name}.pickle"
    metadata_path = BLD / "metadata" / f"metadata_payout_{simulation_name}.pickle"
    figure_path = BLD / "figures"

    task_swap_payout_analysis(data_path, metadata_path, figure_path, simulation_name)
