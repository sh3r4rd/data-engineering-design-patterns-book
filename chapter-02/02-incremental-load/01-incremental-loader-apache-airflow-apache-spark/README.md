# Incremental loader

All the components (dataset generator, Kubernetes with the Spark Operator, Apache Airflow) run in Docker containers;
you don't need a local Python environment, minikube, Helm, or kubectl.

## Data preparation
1. Generate the dataset for the demo:
```
cd dataset
mkdir -p /tmp/dedp/ch02/incremental_loader/output
# the Spark jobs run as the spark user (uid 185) of the job image and write their output here
chmod 777 /tmp/dedp/ch02/incremental_loader/output
docker-compose down --volumes; docker-compose up
```

## Kubernetes and PySpark job preparation
1. Start the Kubernetes cluster:
**⚠️ If you replay the demo, stop Apache Airflow first (see the Cleanup section); it's attached to the network and volume managed by this stack**
```
cd ../kubernetes
docker-compose down --volumes; docker-compose up -d
docker wait dedp_test_incremental_loader_spark_operator_installer
```
The stack runs a single-node [k3s](https://k3s.io/) Kubernetes cluster in a privileged container and installs the
[Spark Operator](https://github.com/kubeflow/spark-operator) with Helm. It also creates:
* the `dedp-ch02` namespace and the `spark-editor` service account used by the Spark jobs
* a Docker network (`dedp_ch02_incremental_loader`) and a volume with the cluster's kubeconfig (`dedp_ch02_incremental_loader_kubeconfig`),
  both used later by Apache Airflow

The dataset directory is mounted in the k3s container as `/data_for_demo`; the Spark jobs access it with a `hostPath`
volume.

The `docker wait` command returns once the Spark Operator is installed; it should print `0`. The first run downloads
the images and can take a few minutes.
2. Build the job Docker image and load it into the Kubernetes cluster:
```
cd ../incremental-spark-job
docker build -t depd_visits_loader .
docker save depd_visits_loader:latest | docker exec -i dedp_test_incremental_loader_k3s ctr -n k8s.io images import -
# check if the the image was correctly loaded
# You should see docker.io/library/depd_visits_loader:latest
docker exec dedp_test_incremental_loader_k3s crictl images | grep depd_visits_loader
```
3. Check the Spark Operator pods; you can also use this command to follow the Spark jobs started by the pipeline:
```
docker exec dedp_test_incremental_loader_k3s kubectl get pods -n dedp-ch02
```
4. Explain the [visits_loader.py](incremental-spark-job%2Fvisits_loader.py)
* it uses the KISS approach to copy JSON files 
* input and output directories come from the data orchestrator; no orchestration-related logic in the job

## Orchestration layer
1. Explain the [visits_incremental_loader.py](airflow%2Fdags%2Fvisits_incremental_loader.py)
* the pipeline starts with a sensor waiting for the next partition to be available; 
  it's our readiness marker 
* next, the job DAG starts the data loading job and quits
* once the job submitted, it runs a sensor to check the job's outcome
💡 by using this `fire & forget` approach, the orchestration resources are freed and can be used for other tasks; otherwise 
the sensor would wait as long as the job didn't complete
2. Start the Apache Airflow instance in a new terminal opened in this demo's directory:
**⚠️ The Kubernetes stack from the previous section must be running; it creates the Docker network and the kubeconfig volume used by Airflow**
```
cd airflow
docker-compose down --volumes; docker-compose up --build
```
The first run builds the image and can take a few minutes. Apache Airflow reaches the Kubernetes API server at
`https://k3s:6443` through the shared Docker network.
3. Access the Web UI at http://localhost:8080/login/ with dedp/dedp as login/password once the webserver has started
4. Enable the `visits_incremental_loader` DAG
![ch02_enable_dag.png](assets%2Fch02_enable_dag.png) 
5. Check the outcome:
```
$ tree /tmp/dedp/ch02/incremental_loader/output
```
You can follow the Spark applications with:
```
docker exec dedp_test_incremental_loader_k3s kubectl get sparkapplications -n dedp-ch02
```

## Cleanup
Run from this demo's directory and stop the stacks in the reverse order (Apache Airflow is attached to the network and
volume of the Kubernetes stack, so it must go first):
```
(cd airflow && docker-compose down --volumes)
(cd kubernetes && docker-compose down --volumes)
(cd dataset && docker-compose down --volumes)
```

