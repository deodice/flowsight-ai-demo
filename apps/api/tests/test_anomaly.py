from app.services.anomaly import explain_anomalies


def test_robust_anomaly_is_explainable():
    anomalies = explain_anomalies([10, 10, 11, 9, 10, 42])
    assert anomalies[0]["observed"] == 42
    assert "above" in anomalies[0]["explanation"]
