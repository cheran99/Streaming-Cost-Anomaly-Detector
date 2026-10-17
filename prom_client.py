import requests


def get_prometheus(promql, label="pod", base_url="http://localhost:9090"):
    response = requests.get(f"{base_url}/api/v1/query", params={"query": promql}, timeout=10)
    data = response.json()
    if data["status"] != "success":
        raise Exception(f"Error querying Prometheus: {response.status_code} - {data.get('error', 'Unknown error')}")
    if "data" not in data or "result" not in data["data"]:
        raise ValueError(f"Unexpected response format: {data}")
    if not data["data"]["result"]:
        raise ValueError(f"No data returned for query: {promql}")
    build_result = {series["metric"][label]: float(series["value"][1]) for series in data["data"]["result"]}
    return build_result


if __name__ == "__main__":
    cpu_util = get_prometheus(promql = f'sum(rate(container_cpu_usage_seconds_total{{namespace="cost-demo", container!=""}}[120s])) by (pod) / sum(kube_pod_container_resource_requests{{namespace="cost-demo", resource="cpu"}}) by (pod)')
    print(cpu_util)