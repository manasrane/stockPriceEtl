CREATE USER superset WITH PASSWORD 'airflow';
CREATE DATABASE superset_db OWNER airflow;
CREATE USER examples WITH PASSWORD 'examples';
CREATE DATABASE examples_db OWNER examples;