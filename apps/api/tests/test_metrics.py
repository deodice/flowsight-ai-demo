from app.services.metrics import fill_rate, forecast_bias, inventory_turns, otif


def test_kpis_handle_normal_and_zero_denominators():
    assert fill_rate(95, 100) == 95
    assert fill_rate(10, 0) == 0
    assert otif(47, 50) == 94
    assert inventory_turns(740000, 100000) == 7.4
    assert forecast_bias([100, 100], [110, 90]) == 0
