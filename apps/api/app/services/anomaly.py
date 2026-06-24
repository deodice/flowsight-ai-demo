import numpy as np


def robust_z_scores(values: list[float]) -> list[float]:
    data = np.asarray(values, dtype=float)
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    if mad == 0:
        return [0.0 for _ in values]
    return (0.6745 * (data - median) / mad).round(3).tolist()


def explain_anomalies(values: list[float], threshold: float = 3.5) -> list[dict]:
    scores = robust_z_scores(values)
    median = float(np.median(values))
    return [
        {
            "index": i, "observed": value, "expected": median, "robust_z": score,
            "direction": "above" if score > 0 else "below",
            "explanation": f"{value:.2f} is {abs(score):.1f} robust deviations {'above' if score > 0 else 'below'} the median {median:.2f}."
        }
        for i, (value, score) in enumerate(zip(values, scores)) if abs(score) >= threshold
    ]
