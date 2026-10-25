from classify import classify_container


def test_missing_avg_is_named():
    data = {
        "peak": {"a": 1.0},
        "avg": {},
        "restarts": {"a": 0},
    }
    result = classify_container("a", data)
    assert result["label"] == "missing-data"
    assert result["reason"] == "Missing metrics: avg"


def test_two_missing_are_joined():
    data = {"peak": {}, "avg": {}, "restarts": {"a": 0}}
    result = classify_container("a", data)
    assert result["reason"] == "Missing metrics: peak, avg"


def test_all_present_uses_classify():
    data = {"peak": {"a": 0.1}, "avg": {"a": 0.05}, "restarts": {"a": 0}}
    result = classify_container("a", data)
    assert result["label"] == "over-provisioned"


def test_missing_restarts_is_named():
    data = {"peak": {"a": 1.0}, "avg": {"a": 0.5}, "restarts": {}}
    result = classify_container("a", data)
    assert result["reason"] == "Missing metrics: restarts"