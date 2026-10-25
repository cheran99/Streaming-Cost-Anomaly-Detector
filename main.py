from prom_client import get_prometheus
from classify import classify_container
from narrate import narrate
from report_html import build_html, save_report


def main():
    promql = {
        "peak" : f'max_over_time(sum(rate(container_cpu_usage_seconds_total{{namespace="cost-demo", container != ""}}[120s]))by (container)[30m:30s]) / sum(kube_pod_container_resource_requests{{namespace="cost-demo", resource="cpu"}}) by (container)',
        "avg" : f'avg_over_time(sum(rate(container_cpu_usage_seconds_total{{namespace="cost-demo", container != ""}}[120s]))by (container)[30m:30s]) / sum(kube_pod_container_resource_requests{{namespace="cost-demo", resource="cpu"}}) by (container)',
        "restarts" : f'sum(increase(kube_pod_container_status_restarts_total{{namespace="cost-demo", container != ""}}[7d])) by (container)',
    }
    data = {}
    
    for key, query in promql.items():
        data[key] = get_prometheus(promql=query)

    containers = data["peak"].keys() | data["avg"].keys() | data["restarts"].keys()
    classification = {}
    report = []
    for container in sorted(containers):
        classification[container] = classify_container(container, data)
        data_results = {"container": container, "peak": data["peak"].get(container), "avg": data["avg"].get(container), "restarts": data["restarts"].get(container), "classification": classification[container]}
        report.append(data_results)
    return report

if __name__ == "__main__":
    container_report = main()
    summary = narrate(container_report)
    page = build_html(container_report, summary)
    path = save_report(page)
    print("File saved to:", path)