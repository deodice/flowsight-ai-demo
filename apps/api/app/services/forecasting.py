import math
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing


def wape(actual: np.ndarray, predicted: np.ndarray) -> float:
    denominator = np.abs(actual).sum()
    return float(np.abs(actual - predicted).sum() / denominator) if denominator else float("inf")


def moving_average(train: np.ndarray, horizon: int, window: int = 4) -> np.ndarray:
    return np.repeat(float(np.mean(train[-min(window, len(train)):])), horizon)


def croston(train: np.ndarray, horizon: int, alpha: float = 0.2) -> np.ndarray:
    demand = np.asarray(train, dtype=float)
    nonzero = np.flatnonzero(demand)
    if not len(nonzero):
        return np.zeros(horizon)
    estimate = demand[nonzero[0]]
    interval = max(nonzero[0] + 1, 1)
    last = nonzero[0]
    for idx in nonzero[1:]:
        estimate = alpha * demand[idx] + (1 - alpha) * estimate
        interval = alpha * (idx - last) + (1 - alpha) * interval
        last = idx
    return np.repeat(estimate / max(interval, 1), horizon)


def exponential(train: np.ndarray, horizon: int) -> np.ndarray:
    fit = SimpleExpSmoothing(train, initialization_method="estimated").fit(optimized=True)
    return np.asarray(fit.forecast(horizon))


def holt_winters(train: np.ndarray, horizon: int) -> np.ndarray:
    seasonal = len(train) >= 24 and np.count_nonzero(train) > len(train) * .5
    fit = ExponentialSmoothing(
        train, trend="add", seasonal="add" if seasonal else None,
        seasonal_periods=12 if seasonal else None, initialization_method="estimated"
    ).fit(optimized=True)
    return np.maximum(0, np.asarray(fit.forecast(horizon)))


def select_forecast(values: list[float], horizon: int = 8) -> dict:
    series = np.asarray(values, dtype=float)
    test_size = min(max(3, len(series) // 5), 8)
    train, test = series[:-test_size], series[-test_size:]
    methods = {
        "moving_average": moving_average,
        "croston": croston,
        "exponential_smoothing": exponential,
        "holt_winters": holt_winters,
    }
    scores: dict[str, float] = {}
    for name, method in methods.items():
        try:
            scores[name] = round(wape(test, method(train, test_size)), 4)
        except Exception:
            scores[name] = math.inf
    selected = min(scores, key=scores.get)
    forecast = methods[selected](series, horizon)
    residual_scale = float(np.std(test - methods[selected](train, test_size))) if test_size else 0
    low = np.maximum(0, forecast - 1.28 * residual_scale)
    high = forecast + 1.28 * residual_scale
    mean_daily = float(np.mean(series[-min(8, len(series)):]))
    lead_time = 14
    safety_stock = 1.65 * float(np.std(series[-min(12, len(series)):])) * math.sqrt(lead_time / 7)
    return {
        "selected_model": selected,
        "scores": scores,
        "forecast": forecast.round(2).tolist(),
        "lower_80": low.round(2).tolist(),
        "upper_80": high.round(2).tolist(),
        "reorder_point": round(mean_daily * (lead_time / 7) + safety_stock, 2),
        "safety_stock": round(safety_stock, 2),
        "methodology": "Rolling holdout WAPE; lowest error wins. Croston is included for intermittent demand."
    }
