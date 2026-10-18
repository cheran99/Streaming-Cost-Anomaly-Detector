SYSTEM_PROMPT = """
   1. Explain each container's classification label that includes reason and warnings. Never change or override the label.
   2. Use only the numbers in the input. Never invent or calculate new ones.
   3. Do not estimate costs; the input contains no cost data.
   4. Mention restarts only when warning is present.
   5. For missing-data / insufficient-data: do not guess a cause or recommend resizing. Recommend checking that Prometheus is collecting metrics for that container instead.
   6. Audience: Site Reliability Engineering team. Keep each container to 2-3 sentences."""


def prepare(report):
    slim = []
    for entry in report:
        c = entry["classification"]
        item = {
            "container": entry["container"],
            "label": c["label"],
            "reason": c["reason"],
        }
        if c["warning"] is not None:
            item["warning"] = c["warning"]
        slim.append(item)
    return slim

if __name__ == "__main__":
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

    checks = [
        (len(slim) == 2, "both containers kept"),
        ("peak" not in slim[0], "raw numbers dropped"),
        ("warning" in slim[0], "warning kept when present"),
        ("warning" not in slim[1], "warning dropped when None"),
    ]
    for passed, name in checks:
        print("PASS" if passed else "FAIL", name)