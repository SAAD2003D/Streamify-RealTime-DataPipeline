 # Streamify
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Google BigQuery](https://img.shields.io/badge/Google%20BigQuery-4285F4?style=for-the-badge&logo=googlebigquery&logoColor=white)](https://cloud.google.com/bigquery)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)

## 📌 Project Overview

**Streamify** is an end-to-end real-time data pipeline that processes user event streams from a simulated music streaming service. It ingests, transforms, and analyzes live user interactions like song plays, navigation, and authentication.

## project architecture :
![image](https://github.com/user-attachments/assets/82081403-fef7-4d34-9d3f-dce3a3b44a86)

## 🚀 **Tech Stack**
- **Event Streaming**: Apache Kafka
- **Stream Processing**: Apache Spark
- **Batch Processing & Orchestration**: Apache Airflow
- **Data Transformation**: dbt
- **Data Storage**: Google Cloud Storage (GCS)
- **Data Warehouse**: BigQuery
- **Infrastructure as Code**: Terraform
- **Containerization**: Docker
- **Visualization**: Google Data Studio

---

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

---

## 🔥 **Project Workflow**
1. **Kafka Producer** generates fake user events using **EventSim**.
2. **Spark Streaming** processes events and stores them in **Google Cloud Storage (GCS)** every 2 minutes.
3. **Apache Airflow** runs hourly batch jobs to move data to **BigQuery**.
4. **dbt** transforms the raw data into structured tables for analytics.
5. **Google Data Studio** visualizes metrics like:
   - 🎵 Most played songs
   - 👥 Active users
   - 🌍 User demographics
   - 🕒 Session durations

---

## ⚙️ **Setup & Deployment**
1. Clone the repository:  
   ```sh
   git clone https://github.com/YOUR_GITHUB_USERNAME/Streamify-RealTime-DataPipeline.git
   cd Streamify-RealTime-DataPipeline
   ```
2. Install dependencies (Docker, Terraform, etc.).
3. Run Kafka producer and Spark Streaming.
4. Deploy Airflow DAGs.
5. Connect BigQuery to Google Data Studio.

---

## 💡 **Contributing**
Feel free to fork the repo, open issues, or submit PRs.

