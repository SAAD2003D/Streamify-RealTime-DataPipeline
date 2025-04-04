 # Streamify


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

