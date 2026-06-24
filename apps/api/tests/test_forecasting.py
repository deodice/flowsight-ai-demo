from app.services.forecasting import select_forecast


def test_forecast_selection_is_transparent_and_bounded():
    values = [80, 84, 89, 91, 96, 101, 99, 106, 111, 115, 118, 124, 127, 132, 136, 141]
    result = select_forecast(values, 6)
    assert result["selected_model"] in result["scores"]
    assert len(result["forecast"]) == 6
    assert all(x >= 0 for x in result["lower_80"])
    assert result["reorder_point"] > 0


def test_intermittent_demand_supports_croston_candidate():
    result = select_forecast([0, 0, 4, 0, 0, 0, 6, 0, 0, 5, 0, 0, 0, 8, 0], 4)
    assert "croston" in result["scores"]
