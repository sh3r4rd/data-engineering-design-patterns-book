FROM python:3.11-slim-bookworm
# bookworm is pinned on purpose: trixie (the current python:3.11-slim) doesn't ship OpenJDK 17
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
# Download the Kafka source jars into the Ivy cache at build time so the job starts without network access;
# like in visits_stream_processor.py, the connector version follows the installed PySpark
RUN python -c "import pyspark; from pyspark.sql import SparkSession; SparkSession.builder.master('local[1]').config('spark.jars.packages', f'org.apache.spark:spark-sql-kafka-0-10_2.12:{pyspark.__version__}').getOrCreate().stop()"
ENV PYTHONUNBUFFERED=1
WORKDIR /app
