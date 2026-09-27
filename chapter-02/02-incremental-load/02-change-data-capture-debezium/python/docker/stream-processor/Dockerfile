FROM python:3.11-slim-bookworm
# bookworm is pinned on purpose: trixie (the current python:3.11-slim) doesn't ship OpenJDK 17
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "pyspark==3.5.0"
# Download the Kafka source jars into the Ivy cache at build time so the job starts without network access
RUN python -c "from pyspark.sql import SparkSession; SparkSession.builder.master('local[1]').config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0').getOrCreate().stop()"
ENV PYTHONUNBUFFERED=1
WORKDIR /app
