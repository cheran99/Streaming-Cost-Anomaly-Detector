import requests


def get_prometheus(promql, label="container", base_url="http://localhost:9090"):
    response = requests.get(f"{base_url}/api/v1/query", params={"query": promql}, timeout=10)
    data = response.json()
    if data["status"] != "success":
        raise RuntimeError(f"Error querying Prometheus: {data["status"]}")
    if "data" not in data or "result" not in data["data"]:
        raise ValueError(f"Unexpected response format: {data}")
    if not data["data"]["result"]:
        raise ValueError(f"No data returned for query: {promql}")
    build_result = {series["metric"][label]: float(series["value"][1]) for series in data["data"]["result"]}
    return build_result


if __name__ == "__main__":
    peak = get_prometheus(promql = f'max_over_time(sum(rate(container_cpu_usage_seconds_total{{namespace="cost-demo", container != ""}}[120s]))by (container)[5m:30s]) / sum(kube_pod_container_resource_requests{{namespace="cost-demo", resource="cpu"}}) by (container)')
    avg = get_prometheus(promql = f'avg_over_time(sum(rate(container_cpu_usage_seconds_total{{namespace="cost-demo", container != ""}}[120s]))by (container)[5m:30s]) / sum(kube_pod_container_resource_requests{{namespace="cost-demo", resource="cpu"}}) by (container)')
    restarts = get_prometheus(promql = f'sum(increase(kube_pod_container_status_restarts_total{{namespace="cost-demo", container != ""}}[7d])) by (container)')
    containers = peak.keys() | avg.keys() | restarts.keys()
    for container in sorted(containers):
        if container in peak and container in avg and container in restarts:
            print(f"{container}: Peak: {peak[container]*100:.2f}%, Average: {avg[container]*100:.2f}%, Restarts: {restarts[container]:.0f}")
        else:
            print(f"Data missing for container: {container}")