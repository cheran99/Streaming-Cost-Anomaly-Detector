from narrate import prepare


def test_warning_dropped_when_none():
    fake_report = [
        {
            "container": "container1",
            "peak": 1.2,
            "avg": 0.5,
            "restarts": 302,
            "classification": {
                "label": "under-provisioned",
                "reason": "Peak CPU usage of 120.00% exceeds requested resources",
                "warning": "302 restarts in the last 7 days"
            }
        },
        {
            "container": "container2",
            "peak": 0.0,
            "avg": 0.0,
            "restarts": 0,
            "classification": {
                "label": "over-provisioned",
                "reason": "Peak CPU usage of 0.00% is significantly below requested resources",
                "warning": None
            }
        },
    ]
    slim = prepare(fake_report)
    assert len(slim) == 2, "both containers kept"
    assert "peak" not in slim[0], "raw numbers dropped"
    assert "warning" in slim[0], "warning kept when present"
    assert "warning" not in slim[1], "warning dropped when None"