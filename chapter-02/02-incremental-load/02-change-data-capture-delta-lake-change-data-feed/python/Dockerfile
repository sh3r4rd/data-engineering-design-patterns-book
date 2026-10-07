FROM python:3.11-slim-bookworm
# bookworm is pinned on purpose: trixie (the current python:3.11-slim) doesn't ship OpenJDK 17
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
# Download the Delta Lake jars into the Ivy cache at build time so the job starts without network access
RUN python -c "from delta import configure_spark_with_delta_pip; from pyspark.sql import SparkSession; configure_spark_with_delta_pip(SparkSession.builder.master('local[1]')).getOrCreate().stop()"
ENV PYTHONUNBUFFERED=1
WORKDIR /app
