def safe_rate(numerator: float, denominator: float) -> float:
    return 0.0 if denominator <= 0 else round(100 * numerator / denominator, 2)


def fill_rate(shipped: float, ordered: float) -> float:
    return safe_rate(shipped, ordered)


def otif(on_time_and_full: int, total_deliveries: int) -> float:
    return safe_rate(on_time_and_full, total_deliveries)


def forecast_bias(actual: list[float], forecast: list[float]) -> float:
    denominator = sum(actual)
    return 0.0 if not actual or denominator == 0 else round(100 * sum(f - a for a, f in zip(actual, forecast)) / denominator, 2)


def inventory_turns(annualized_cogs: float, average_inventory: float) -> float:
    return 0.0 if average_inventory <= 0 else round(annualized_cogs / average_inventory, 2)
