import itertools
from datetime import date, datetime
from typing import Any, Generator, Union

import requests

URL_BASE = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
DEFAULT_LIMIT = 200
TIPO_FUNDO = 1
ID_CATEGORIA_DOCUMENTO = 14


def get_query_params(
    reference_date: Union[str, date, datetime],
    page: int,
) -> dict[str, Any]:
    """
    Retorna os parâmetros da query.
    """
    if isinstance(reference_date, (date, datetime)):
        reference_date = reference_date.strftime("%d/%m/%Y")

    return {
        "d": 0,
        "s": page * DEFAULT_LIMIT,
        "l": DEFAULT_LIMIT,
        "tipoFundo": TIPO_FUNDO,
        "idCategoriaDocumento": ID_CATEGORIA_DOCUMENTO,
        "dataReferencia": reference_date,
    }


def fetch_data_page(url: str, params: dict[str, Any]) -> Union[Any, None]:
    """
    Busca uma página de dados da URL.
    """
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Erro na requisição: {response.status_code}")
        return None


def generate_data_pages(reference_date: Union[str, date, datetime]) -> Generator[Any, Any, None]:
    """
    Gera páginas de dados.
    """
    page = 0
    while True:
        params = get_query_params(reference_date, page)
        data_page = fetch_data_page(URL_BASE, params)

        if not data_page:
            break

        yield data_page
        page += 1


def merge_pages_data(reference_date: date) -> list[Any]:
    """
    Combina todas as páginas de dados em uma lista.
    """
    data_pages = generate_data_pages(reference_date)
    return list(itertools.chain.from_iterable(data_pages))
