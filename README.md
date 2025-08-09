 # Streamify
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
![Apache Airflow Logo](https://cdn.simpleicons.org/apacheairflow/017CEE)
[![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Google BigQuery](https://img.shields.io/badge/Google%20BigQuery-4285F4?style=for-the-badge&logo=googlebigquery&logoColor=white)](https://cloud.google.com/bigquery)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)

## 📌 Project Overview

**Streamify** is an end-to-end real-time data pipeline that processes user event streams from a simulated music streaming service. It ingests, transforms, and analyzes live user interactions like song plays, navigation, and authentication.

## project architecture :
![image](https://github.com/user-attachments/assets/82081403-fef7-4d34-9d3f-dce3a3b44a86)

## 📂 **Repository Structure**
```plaintext
📂 kafka-producer/       # Kafka event simulation (EventSim setup)
📂 spark-streaming/      # Spark Streaming scripts for processing Kafka data
📂 airflow-dags/        # Apache Airflow DAGs for batch processing
📂 dbt-models/          # dbt models for transforming data in BigQuery
📂 terraform/           # Terraform scripts for provisioning GCP resources
📂 docker/              # Docker setup for local deployment
📂 datasets/            # MillionSongSubset (small sample)
📂 notebooks/           # Jupyter notebooks for data analysis & validation
📜 README.md            # Project Overview
```

