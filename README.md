[Stock Analytics Pipeline](https://github.com/manasrane/stockPriceETL)
📈 Stock Market Dashboards
This project features interactive dashboards for visualizing stock market data using Apache Superset, Airflow, PostgreSQL, and APIs from Alpha Vantage. It includes:

🗓️ Stock-Monthly Dashboard
<img width="1847" height="942" alt="image" src="https://github.com/user-attachments/assets/a41408ef-87d7-4a08-97ec-c4caa3f4517b" />
🌍 Global Stock Dashboard
<img width="1220" height="332" alt="image" src="https://github.com/user-attachments/assets/c5683fec-a156-474e-b7db-d71e291542ea" />
⏱️ Intra-Day Dashboard
<img width="1846" height="901" alt="image" src="https://github.com/user-attachments/assets/70b26322-9979-42ac-bd8e-485da158d96e" />
🧩 Tech Stack
Data Source: Alpha Vantage API https://www.alphavantage.co/documentation/

ETL Orchestration: Apache Airflow

Storage: PostgreSQL

Dashboarding: Apache Superset

Backend Language: Python

Stock-Monthly Dashboard

Global Stock dashboard

Intra-Day Dashboard

⚙️ How to Run Locally with Docker
🧰 Prerequisites
Docker and Docker Compose installed

🗂️ Folder Structure
bash
Copy
Edit
project/

├── airflow/

│   ├── dags/

│   └── Dockerfile

├── postgres/

│   └── init.sql

├── superset/

│   └── Dockerfile

├── docker-compose.yml

├── .env

└── requirements.txt

🚀 Steps to Run
Clone the repo

bash
Copy
Edit
git clone https://github.com/manasrane/your-repo-name.git
cd your-repo-name
Set Alpha Vantage API key in .env

ini
Copy
Edit
ALPHAVANTAGE_API_KEY=your_key_here
Start all services

bash
Copy
Edit
docker-compose up --build
Access the services

Airflow: http://localhost:8080

Superset: http://localhost:8088

PostgreSQL: localhost:5432

Trigger ETL Pipeline

Login to Airflow and run the DAG (e.g., stock_etl_dag)

View Dashboards

Login to Superset, import dashboards if not already present.
