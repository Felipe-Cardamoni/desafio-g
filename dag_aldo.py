from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook
import mysql.connector
import requests
import json
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

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


def extract_porte(descricao):
    match = re.search(r"(\d+(?:,\d+)?)KWP", descricao)
    if match:
        porte = f"{match.group(1)} kWp"
        return porte
    return None


def get_filter_id():
    url_get_filter_id = "https://www.aldo.com.br/wcf/Produto.svc/getfiltrosporsegmento"
    payload_get_filter_id = {
        "slug": "energia-solar",
        "origem": "categoria"
    }
    response_get_filter_id = requests.post(url_get_filter_id, json=payload_get_filter_id)
    filter_id = response_get_filter_id.json().get("FilterId")
    return filter_id


def get_products(filter_id):
    url_get_products = "https://www.aldo.com.br/wcf/Produto.svc/getprodutosporsegmentonotlogin"
    products_data = []  # Lista para armazenar os dados dos produtos
    for page in range(10):
        payload_get_products = {
            "offset": page,
            "filterId": filter_id,
            "orderby": "2"
        }
        response_get_products = requests.post(url_get_products, json=payload_get_products)
        products = response_get_products.json()
        for product in products:
            prd_descricao = product.get("prd_descricao")
            prd_preco = product.get("prd_preco")
            porte = extract_porte(prd_descricao)
            estrutura = ''

            product_data = {
                "porte": porte,
                "estrutura": estrutura,
                "preco": prd_preco
            }
            products_data.append(product_data)
        print(f"Page {page + 1} processed.")

    # Gravar os dados em um arquivo JSON
    with open("products_data.json", "w") as file:
        json.dump(products_data, file)
    return products_data


def insert_data():
    with open("products_data.json", "r") as file:
        products_data = json.load(file)

    connection = mysql_connect()
    if connection:
        try:
            cursor = connection.cursor()

            # Inserir os dados na tabela
            for product_data in products_data:
                porte = product_data.get("porte")
                estrutura = product_data.get("estrutura")
                preco = product_data.get("preco")

                sql = "INSERT INTO tb_produtos (porte_produto, estrutura, preco) VALUES (%s, %s, %s)"
                values = (porte, estrutura, preco)
                cursor.execute(sql, values)
                connection.commit()
                print("Dados inseridos na tabela 'tb_produtos' com sucesso.")

        except Exception as e:
            print("Erro ao inserir dados na tabela 'tb_produtos':", str(e))
        finally:
            # Fechar a conexão
            connection.close()


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 6, 26, 8, 0),  # Data de início às 8:00 da manhã
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('dados_api_aldo', default_args=default_args, schedule_interval="0 8 * * *")  # Executar diariamente às 8:00

task_extract_data = PythonOperator(
    task_id='extract_data',
    python_callable=get_filter_id,
    dag=dag,
)

task_process_data = PythonOperator(
    task_id='process_data',
    python_callable=get_products,
    op_kwargs={'filter_id': '{{ task_instance.xcom_pull(task_ids="extract_data") }}'},
    dag=dag,
)

task_insert_data = PythonOperator(
    task_id='insert_data',
    python_callable=insert_data,
    dag=dag,
)

task_extract_data >> task_process_data >> task_insert_data
