# Streaming Cost Anomaly Detector

## Overview

Due to poor CPU sizing, streaming platforms waste money in Kubernetes when their containers are over-provisioned or risk performance when containers are under-provisioned. It goes unnoticed because nothing alerts on waste, only failures. This tool pulls CPU metrics from Prometheus and classifies each container's CPU sizing using fixed rules, while Claude explains each result in plain English. The output is an HTML report with a facts table plus a short explanation per container which the SRE team can scan in under a minute.

## Sample Output

![alt text](sample-report_2026-10-25_00-35.png)

`checkout-api` is over-provisioned, `recommendation-engine` is bursty and `video-transcoder` is right-sized. My code builds the table and decides the labels, and Claude only writes the explanations from labels, reasons, and restart warnings.

## How It Works

```mermaid
flowchart TD
    K([kind cluster: cost-demo]) -->|CPU and restarts, every 30s| A[(Prometheus)]
    A --> |port-forward :9090|B[prom_client.py]
    B --> C[classify.py]
    C --> D[narrate.py]
    D --> |labels, reasons, warnings|E([Claude API])
    E --> |explanations|F[report_html.py]
    C --> |facts table|F
    F --> G[reports/]  
```

`report_html.py` has two inputs on purpose: `classify.py` decides the labels and `report_html.py` builds the table, so every number in the table comes from my code. Claude only writes explanations, so even if it gets something wrong, the values in the table stay correct.

## Tech Stack

| Technology | Purpose |
|---|---|
| Kubernetes (`kind`) | Runs a single-node local cluster with three demo workloads in the `cost-demo` namespace |
| Docker | Runs the kind cluster as a container |
| Helm | Installs Prometheus into the `kind` cluster via the `kube-prometheus-stack` chart |
| Prometheus | Scrapes CPU and restart metrics from `kind` |
| Python `3.12` | Runs the anomaly detector tool |
| Claude API | Uses Haiku 5.5 as the model to easily explain the classifications for each container after the classifier already made the decisions |
| markdown | Converts Claude’s written explanation into HTML for the report |
| pytest | Tests the classification rules, missing data, and prompt slimming without requiring a cluster or API key |


## How To Run It

### Prerequisites 
- Docker Desktop 
- Windows Subsystem for Linux (WSL) (Windows only)
- Git
- Python - `3.12` or newer
- kind
- kubectl
- Helm
- Anthropic API key (see Step 6)

### Step 1 - Clone the repo:

- Clone this repository to your local machine:

    ```
    git clone https://github.com/<your-username>/Streaming-Cost-Anomaly-Detector
    ```

- `<your-username>` acts as a placeholder for your GitHub username.
- Change to the working directory where this repository is stored:

    ```
    cd Streaming-Cost-Anomaly-Detector
    ```

### Step 2 - Create `kind` cluster:

- Name your cluster cost-anomaly-demo:

    ```
    kind create cluster --name cost-anomaly-demo
    ```

- Run kubectl to confirm the cluster is running and kubectl is pointed towards it:

    ```
    kubectl get nodes

    kubectl cluster-info 
    ```

- Create a namespace:

    ```
    kubectl create namespace cost-demo
    ```

### Step 3 - Deploy three workloads:

- The three workloads to deploy are deliberately configured to demonstrate each label and are found in the `manifests/` directory:
    - `checkout-api`
    - `recommendation-engine`
    - `video-transcoder`

- Ensure the manifest YAMLs are set to `namespace: cost-demo`

- Apply the manifests:

    ```
    kubectl apply -f manifests/
    ```

- After about a minute, check that the workloads are running:

    ```
    kubectl get pods -n cost-demo
    ```

### Step 4 - Install Prometheus into the kind cluster via Helm:

- Create another namespace different from `cost-demo`:

    ```
    kubectl create namespace monitoring
    ```

- Install Prometheus:

    ```
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

    helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
    --namespace monitoring
    ```


### Step 5 - Port-forward `kube-prometheus-stack` service to Prometheus UI:

- Check the list of pods that are running along with the list of network services configured for them in the `monitoring` namespace:

    ```
    kubectl get pods -n monitoring
    kubectl get svc -n monitoring
    ```

- Wait until `kubectl get pods -n monitoring` shows everything `Running`.

- Find the network service with port `9090` and a ClusterIP that isn’t `None` (the prometheus-operated service is headless, so skip it) to connect to Prometheus UI:

    ```
    kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090
    ```

- Leave the port-forward running and open another terminal for the following steps.

### Step 6 - Set up your Claude API key: 

- Create a file named `.env` in the repo root.
- Add `.env` to `.gitignore` before pasting the key.
- Run `git check-ignore .env`, which should print `.env` if it’s ignored.
- To get the Claude API key, go to: https://console.anthropic.com
- Go to API Keys and click Create Key.
- Copy the key straight away and paste it into the `.env` file:
    ```
    ANTHROPIC_API_KEY=sk-ant-...
    ```

### Step 7 - Run the detector tool:

- Wait at least 30-45 minutes after completing Step 4 before running this particular step so that Prometheus has enough data for the first report, otherwise it will look empty. This is because the PromQL queries use 30-minute windows.

- Create and activate the virtual environment:

    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```

- Install the dependencies in `requirements.txt`:

    ```
    pip3 install -r requirements.txt
    ```

- Run `main.py`:

    ```
    python3 main.py
    ```

- Open the latest report saved in `reports/`.

### Step 8 - Cleanup

- Delete the `kind` cluster:

    ```
    kind delete cluster --name cost-anomaly-demo
    ```


## Key Decisions



## What I'd Do Differently/Next 