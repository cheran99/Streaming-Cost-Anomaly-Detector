import pytest
from classify import classify


@pytest.mark.parametrize("peak, avg, restarts, expected", [
    (1.2, 0.5, 301.7, "under-provisioned"),
    (0.0, 0.0, 301.7, "over-provisioned"),
    (1.0, 0.9, 301.7, "right-sized"),
    (0.3, 0.0, 301.7, "insufficient-data"),
    (0.99, 0.41, 301.7, "bursty"),
    (0.99, 0.66, 301.7, "right-sized"),
    (0.99, 0.66, 5.0, "right-sized"),
    (0.99, 0.66, 0.0, "right-sized"),
])
def test_classify(peak, avg, restarts, expected):
    assert classify(peak, avg, restarts)["label"] == expected


@pytest.mark.parametrize("restarts, expects_warning", [
    (6.0, True),
    (5.0, False),
    (0.0, False),
])
def test_restart_warning(restarts, expects_warning):
    result = classify(0.99, 0.66, restarts)
    assert (result["warning"] is not None) == expects_warning