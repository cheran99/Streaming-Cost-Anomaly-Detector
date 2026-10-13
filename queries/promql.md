# Query 1:
- The fraction of reserved memory a pod is using right now is divided by how much memory was requested.
- The readings, for example, `0.0049` means that a pod is using 0.49% of reserved memory.

```
sum(container_memory_working_set_bytes{namespace="cost-demo", container != ""}) by (pod)
/
sum(kube_pod_container_resource_requests{namespace="cost-demo", resource="memory"}) by (pod)
```

# Query 2:
- The total CPU requested by pods is measured against the node's total allocatable CPU.
- The readings, for example, `0.583` means that `cost-demo` workloads have reserved 58.3% of the node's CPU (so about 7 out of 12 cores).
- The numerator only counts `cost-demo` pods.

```
sum(kube_pod_container_resource_requests{namespace="cost-demo", resource="cpu"})
/
sum(kube_node_status_allocatable{resource="cpu"})
```

# Query 3:
- The core, highest, and average value of CPU cores a pod is actually burning is measured against the number of cores it requested over the course of 2-5 minutes.
- The small gap between peak and average values means the container is steady, the large gap means the container is bursty, and if the peak value is as low as zero, the container is overprovisioned.
- The window for core values is 120s so that `rate()` has enough samples scraped at 30s intervals while for peak and average values, it is 5 minutes. 

## Query 3a: Core CPU Utilisation:
```
sum(rate(container_cpu_usage_seconds_total{namespace="cost-demo", container != ""}[120s]))by (pod)
/
sum(kube_pod_container_resource_requests{namespace="cost-demo", resource="cpu"}) by (pod)
```

## Query 3b: Peak CPU:
```
max_over_time(sum(rate(container_cpu_usage_seconds_total{namespace="cost-demo", container != ""}[120s]))by (pod)[5m:30s])
/
sum(kube_pod_container_resource_requests{namespace="cost-demo", resource="cpu"}) by (pod)
```

## Query 3c: Average CPU:
```
avg_over_time(sum(rate(container_cpu_usage_seconds_total{namespace="cost-demo", container != ""}[120s]))by (pod)[5m:30s])
/
sum(kube_pod_container_resource_requests{namespace="cost-demo", resource="cpu"}) by (pod)
```

# Query 4:
- The number of restarts of each workload's container is measured over the last 7 days.
- The `sum` of container restarts are grouped by `container` instead of `pod` so that number survives redeploys over a 7 day period.
- The `increase()` also counts the restarts of pods that were deleted over the past 7 days because the Prometheus keeps the old pod's time series until retention expires, hence why `increase()` sees its samples.
- `sum()` of restarts grouped by `containers` adds the old and new pods' counts together.

```
sum(increase(kube_pod_container_status_restarts_total{namespace="cost-demo", container != ""}[7d])) by (container)
```