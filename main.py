from prom_client import get_prometheus
from classify import classify


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
        if container in data["peak"] and container in data["avg"] and container in data["restarts"]:
            classification[container] = classify(peak=data["peak"][container], avg=data["avg"][container], restarts=data["restarts"][container])
        else:
            classification[container] = {"label": "missing-data", "reason": "Missing data for peak, avg, or restarts", "warning": None}

        data_results = {"container": container, "peak": data["peak"].get(container), "avg": data["avg"].get(container), "restarts": data["restarts"].get(container), "classification": classification[container]}
        print(data_results)
        report.append(data_results)
    return report

if __name__ == "__main__":
    main()