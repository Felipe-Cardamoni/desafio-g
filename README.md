# desafio-g
Projeto com foco em web scrapping, utilizando ETL e armazenamento de dados no banco de dados MySQL.

Você deve desenvolver um pipeline de dados que seja capaz de realizar o processo de ETL em duas fontes de dados. As etapas a serem realizadas são descritas a seguir:

Etapa 1 - Configuração de um ambiente para realizar o ETL. O ambiente pode contar com ferramentas de suporte ao processo como Python, Virtualenv, Docker, Apache Airflow, MySQL, Postgres, entre outros.

Etapa 2 - Coleta de dados:

Fonte Solplace: Realize o Web Scraping que faça a coleta informações dos produtos disponíveis (Porte, preço e estrutura) no site https://www.solplace.com.br/shop. Utilizando para isso ferramentas como: Selenium, Scrapy, Beautiful Soup, entre outros.

Fonte Aldo - Realize o Web Scraping para coleta das informações dos produtos disponíveis (Porte e preço) no site da Aldo: https://www.aldo.com.br/categoria/energia-solar/gerador-de-energia-solar-fotovoltaico/on-gr. Porém, obrigatoriamente neste caso, os dados devem ser consumidos via API.

Etapa 3 - Criar uma automação para realizar o processo diariamente.

Etapa 4 - Salvar os dados em uma base estruturada. (não é necessário salvar um histórico de dados, somente o atual)

Etapa 5 - Agrupar os dados das duas fontes em uma tabela que será utilizada em ambiente de produção.
