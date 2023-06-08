import math
from datetime import datetime
from functools import lru_cache
from typing import Generator
from urllib.parse import urlencode

import requests
import scrapy
from scrapy.http import TextResponse


class FnetRequest:
    base_url = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
    itens_por_pagina = 200

    @classmethod
    def build_url(cls, inicio: int = 0) -> str:
        request_params = dict(
            d=1,  # Número de requisições
            s=inicio,  # Começo da requisição
            l=cls.itens_por_pagina,  # Número de registros por requisição
            tipoFundo=1,  # FII
            idCategoriaDocumento=14,  # AVISO_AOS_COTISTAS_ESTRUTURADO
        )
        encoded_params = urlencode(request_params)
        return f"{cls.base_url}?{encoded_params}"

    @classmethod
    @lru_cache
    def calculate_num_pages(cls) -> int:
        response = requests.get(url=cls.build_url()).json()
        total = int(response["recordsTotal"])
        num_pages = math.ceil(total / cls.itens_por_pagina)
        return num_pages

    @classmethod
    def urls(cls) -> Generator[str, None, None]:
        num_paginas = cls.calculate_num_pages()
        for num_pagina in range(num_paginas):
            inicio = num_pagina * cls.itens_por_pagina
            yield cls.build_url(inicio)


class FnetDocumentosScraper(scrapy.Spider):
    name = "fnet_documentos"
    base_url = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    today = datetime.today().strftime("%Y-%m-%d")

    custom_settings = {
        "LOG_FILE": f"logs/{name}/{name}_{now}.log",
        "LOG_LEVEL": "DEBUG",
        "FEEDS": {
            "s3://bronze/%(name)s/reference_date=%(today)s/%(name)s.json": {
                "format": "json",
                "encoding": "utf8",
                "indent": None,
            },
        },
        "EXTENSIONS": {
            "fiis_crawler.extensions.s3_logger.S3Logger": 300,
        },
        "S3_LOG": {
            "ENABLED": True,
            "S3_BUCKET": "silver",
        },
    }

    def start_requests(self):
        for url in FnetRequest.urls():
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response: TextResponse, **kwargs):
        yield from response.json()["data"]  # type: ignore
