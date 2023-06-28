import scrapy
import re


class ProductsSpider(scrapy.Spider):
    name = 'produtos'
    start_urls = [
        'https://www.solplace.com.br/shop',
        'https://www.solplace.com.br/shop/page/2',
        'https://www.solplace.com.br/shop/page/3',
        'https://www.solplace.com.br/shop/page/4',
        'https://www.solplace.com.br/shop/page/5',
        'https://www.solplace.com.br/shop/page/6',
        'https://www.solplace.com.br/shop/page/7'
    ]

    def parse(self, response):
        seen_products = set()

        produto_selectors = response.css('#products_grid .text-truncate')
        preco_selectors = response.css('.oe_currency_value')

        for produto_selector, preco_selector in zip(produto_selectors, preco_selectors):
            produto = produto_selector.css('.text-truncate::text').get()
            preco = preco_selector.css('::text').get()

            if produto and produto.strip() and produto not in seen_products:
                seen_products.add(produto)
                produto_parts = produto.strip().split(" - ", 1)
                porte = produto_parts[0].strip()
                estrutura = produto_parts[1].strip() if len(produto_parts) > 1 else ""

                if preco:
                    preco = preco.replace(',', '')  # Remove a vírgula
                    preco = preco.replace('.', '')  # Remove pontos
                    preco = preco.replace(',', '.')  # Substitui vírgula por ponto
                    preco = float(preco)  # Converte para numérico

                # Extrair valor numérico e unidade de medida do porte
                match = re.search(r'([\d,\.]+)\s*kWp', porte)
                if match:
                    porte = match.group(1).replace(',', '.') + ' kWp'

                yield {
                    'porte': porte,
                    'estrutura': estrutura,
                    'preco': preco
                }
