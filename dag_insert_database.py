import json
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook


def read_data_from_json():
    with open('/home/felipe/Documentos/desafio/airflow/greener/greener/spiders/produtos.json', 'r') as file:
        data = json.load(file)
    return data


def insert_data_to_mysql():
    data = read_data_from_json()
    mysql_hook = MySqlHook(mysql_conn_id='mysql_conn')
    
    for produto in data:
        porte = produto['porte']
        estrutura = produto['estrutura']
        preco = produto['preco']
        
        # Inserir os dados na tabela tb_produtos
        query = f"INSERT INTO tb_produtos (porte, estrutura, preco) VALUES ('{porte}', '{estrutura}', {preco})"
        mysql_hook.run(query)


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 6, 27),
}

with DAG('CollectAndInsertData', default_args=default_args, schedule_interval=None) as dag:
    collect_data = PythonOperator(
        task_id='collect_data',
        python_callable=insert_data_to_mysql,
    )

collect_data
