from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook
import mysql.connector
import subprocess
import json
import os


def mysql_connect():
    try:
        mysql_connect = BaseHook.get_connection("mysql_connect")
        host = mysql_connect.host
        user = mysql_connect.login
        password = mysql_connect.password
        database = mysql_connect.schema

        # Estabelecer conexão com o banco de dados MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Exception as e:
        print("Erro ao conectar com o MySQL:", str(e))
        return None


def run_scrapy_spider():
    current_dir = os.getcwd()
    spider_dir = "/home/felipe/Documentos/desafio/airflow/greener/greener/spiders/"

    try:
        os.chdir(spider_dir)  # Change to the spider directory

        subprocess.run(['scrapy', 'crawl', 'produtos'])
    finally:
        print("Processo realizado")


def insert_data_to_mysql():
    with open('/home/felipe/Documentos/desafio/airflow/greener/greener/spiders/produtos.json') as json_file:
        data = json.load(json_file)

    connection = mysql_connect()
    if connection:
        try:
            cursor = connection.cursor()

            for produto in data:
                porte = produto.get("porte")
                estrutura = produto.get("estrutura")
                preco = produto.get("preco")

                # Inserir os dados na tabela tb_produtos
                query = "INSERT INTO tb_produtos (porte_produto, estrutura, preco) VALUES (%s, %s, %s)"
                values = (porte, estrutura, preco)
                cursor.execute(query, values)
                connection.commit()

            # Fechar o cursor
            cursor.close()

        except Exception as e:
            print("Erro ao inserir dados no MySQL:", str(e))

        finally:
            # Fechar a conexão
            connection.close()


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 6, 27, 8, 0),  # Data de início às 8:00 da manhã
}

with DAG('spider_solplace', default_args=default_args, schedule_interval='0 8 * * *') as dag:
    execute_spider = PythonOperator(
        task_id='execute_spider',
        python_callable=run_scrapy_spider,
    )

    insert_data = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data_to_mysql,
    )

    execute_spider >> insert_data
