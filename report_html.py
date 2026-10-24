import markdown
import os
import html
from datetime import datetime


CSS = """
body {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    max-width: 960px;
    margin: 40px auto;
    padding: 0 24px;
    line-height: 1.6;
}
h1 {
    font-size: 28px;
    font-weight: bold;
    color: #58a6ff;
    border-bottom: 2px solid #21262d;
    padding-bottom: 12px;
}
h2 {
    color: #f0883e;
    font-size: 20px;
    margin-top: 32px;
}
h3 {
    color: #7ee787;
    font-size: 16px;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 14px;
}
th, td {
    border: 1px solid #30363d;
    padding: 10px 14px;
    text-align: left;
}
th {
    background-color: #161b22;
    color: #58a6ff;
    font-weight: 600;
}
tr:nth-child(even) {
    background-color: #161b22;
}
ul, ol {
    padding-left: 24px;
}
li {
    margin: 4px 0;
}
code {
    background-color: #161b22;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    color: #f85149;
}
p {
    margin: 12px 0;
}
"""


def fmt_pct(value):
    if value is None:
        return "N/A"
    return f"{value:.2%}"


def fmt_restarts(value):
    if value is None:
        return "N/A"
    return f"{value:.0f}"


def build_html(report, narrative):
    now = datetime.now()
    formatted_date = now.strftime("%d-%m-%Y, %H:%M")
    rows = ""
    for item in report:
        rows += f"<tr><td>{html.escape(item['container'])}</td><td>{html.escape(item['classification']['label'])}</td><td>{fmt_pct(item['peak'])}</td><td>{fmt_pct(item['avg'])}</td><td>{fmt_restarts(item['restarts'])}</td></tr>"

    narrative_body = markdown.markdown(html.escape(narrative))

    return f"""<html>
    <head>
    <title>
    Container CPU Usage Report
    </title>
    <style>
    {CSS}
    </style>
    </head>
    <body>
    <h1>
    Container CPU Usage Report: {formatted_date}
    </h1>
    <table>
    <tr><th>Container</th><th>Classification: Label</th><th>Peak</th><th>Average</th><th>Restarts</th></tr>
    {rows}
    </table>
    {narrative_body}
    </body>
    </html>
    """


def save_report(html_text):
    os.makedirs("reports", exist_ok=True)
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H-%M")
    path = f"reports/report_{formatted_date}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_text)
    return path

if __name__ == "__main__":
    fake_report = [
        {
            "container": "checkout-api",
            "peak": 0.997,
            "avg": 0.0,
            "restarts": 5.4,
            "classification": {"label": "over-provisioned", "reason": "...", "warning": None},
        },
        {
            "container": "mystery-svc", 
            "peak": None, 
            "avg": None, 
            "restarts": None,
            "classification": {"label": "missing-data", "reason": "Missing data for peak, avg, or restarts", "warning": None}
        },
        {
            "container": "<script>alert(1)</script>", 
            "peak": None, 
            "avg": None, 
            "restarts": None,
            "classification": {"label": "missing-data", "reason": "Missing data for peak, avg, or restarts", "warning": None}
        },
    ]

    page = build_html(fake_report, "dummy narrative")
    print(page)
    print("PASS" if "100%" in page else "FAIL", "known peak shown")
    print("PASS" if "N/A" in page else "FAIL", "missing shown as N/A")
    missing_row = page.split("mystery-svc")[1]
    print("PASS" if "0%" not in missing_row else "FAIL", "missing row has no fake 0%")
    print("PASS" if "<script>" not in page else "FAIL", "raw script tag absent")
    print("PASS" if "&lt;script&gt;" in page else "FAIL", "escaped script present")
    evil = build_html(fake_report, "<b>hi</b>")
    print("PASS" if "<b>hi</b>" not in evil else "FAIL", "narrative escaped")
    print("PASS" if "<h1>" in page else "FAIL", "title shown")