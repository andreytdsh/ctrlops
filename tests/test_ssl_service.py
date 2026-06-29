from ctrlops.services.ssl_service import calculate_ssl_status


def test_ssl_status_calculation():
    assert calculate_ssl_status(60) == "OK"
    assert calculate_ssl_status(30) == "WARNING"
    assert calculate_ssl_status(1) == "WARNING"
    assert calculate_ssl_status(0) == "EXPIRED"
    assert calculate_ssl_status(-2) == "EXPIRED"
