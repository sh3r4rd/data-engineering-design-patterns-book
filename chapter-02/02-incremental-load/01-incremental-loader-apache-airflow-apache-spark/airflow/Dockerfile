FROM apache/airflow:2.9.0-python3.11
# Keep the provider below 7.14.0: from that version SparkKubernetesOperator waits for the Spark job to finish
# and doesn't return the SparkApplication anymore, which breaks the fire & forget + SparkKubernetesSensor pattern
RUN pip install --no-cache-dir "apache-airflow==2.9.0" "apache-airflow-providers-cncf-kubernetes==7.13.0"
