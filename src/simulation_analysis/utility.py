def get_total_exchange_rate_change(raw_data):
    total_change = raw_data.sum(axis="columns").to_frame(name="Final exchange rate")
    return total_change
