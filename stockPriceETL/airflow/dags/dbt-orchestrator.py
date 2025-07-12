import sys
from airflow import DAG
from datetime import datetime,timedelta
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import PythonOperator
from docker.types import Mount
sys.path.append("/opt/airflow/api-request")
from insertRecords import main 
default_args = { 
    'description':'a DAG to orchestrate data',
    'start_date': datetime(2025,4,30),
    'catchup':False,
    }
dag = DAG(
    dag_id ='weather-dbt-orchestrator',
    default_args = default_args,
    schedule=timedelta(minutes=5),  # ✅ correct new syntax
    tags=['dbt', 'weather'],
)

with dag:
    task1 = PythonOperator(
        task_id ='ingest_data_task',
        python_callable = main
    )

    task2 = DockerOperator(
    task_id='transform_data_task',
    image='dbt-local',
    command='run',
    working_dir='/usr/app',
    mounts=[  # lowercase 'mounts'
        Mount(source='/root/repos/weatherApi/dbt/my_project',
              target='/usr/app',
              type='bind'),
        Mount(source='/root/repos/weatherApi/dbt',
              target='/root/.dbt',
              type='bind'),
        Mount(source='/root/repos/weatherApi/dbt/.dbt/profiles.yml',
              target='/root/.dbt/profiles.yml',
              type='bind'),      
    ],
    mount_tmp_dir=False,  # disable default tmp mount :contentReference[oaicite:2]{index=2}
    network_mode='weatherapi_my-network',
    docker_url='unix://var/run/docker.sock',
    auto_remove="success",  # must be bool, not string :contentReference[oaicite:3]{index=3},
    docker_conn_id=None,
    force_pull=False,
    dag=dag
)
