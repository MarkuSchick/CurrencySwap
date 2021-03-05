""" includes utility functions
used in the analysis task_swap_payout.py/task_swap_payout_analysis.py"""


def get_total_exchange_rate_change(raw_data):
    total_change = raw_data.sum(axis="columns")
    return total_change


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
