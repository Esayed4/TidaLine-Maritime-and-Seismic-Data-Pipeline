FROM apache/airflow:latest
USER root

RUN apt-get update && \
    apt-get -y install git curl wget openjdk-17-jdk && \
    apt-get clean

# Install Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-4.1.1/spark-4.1.1-bin-hadoop3.tgz && \
    tar -xzf spark-4.1.1-bin-hadoop3.tgz -C /opt/ && \
    mv /opt/spark-4.1.1-bin-hadoop3 /opt/spark && \
    rm spark-4.1.1-bin-hadoop3.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
    apache-airflow-providers-postgres \
    psycopg2-binary \
    apache-airflow-providers-apache-spark