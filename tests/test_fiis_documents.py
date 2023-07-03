from datetime import date

import pytest
import requests_mock

from fiis_scraper.documentos.crawl import (
    URL_BASE,
    fetch_data_page,
    generate_data_pages,
    get_query_params,
    merge_pages_data,
)


@pytest.mark.parametrize(
    "reference_date, page, expected",
    [
        (
            "01/01/2023",
            0,
            {
                "d": 0,
                "s": 0,
                "l": 200,
                "tipoFundo": 1,
                "idCategoriaDocumento": 14,
                "dataReferencia": "01/01/2023",
            },
        ),
        (
            date(2023, 1, 1),
            1,
            {
                "d": 0,
                "s": 200,
                "l": 200,
                "tipoFundo": 1,
                "idCategoriaDocumento": 14,
                "dataReferencia": "01/01/2023",
            },
        ),
    ],
)
def test_get_query_params(reference_date, page, expected):
    assert get_query_params(reference_date, page) == expected


@pytest.mark.parametrize(
    "status_code, expected",
    [
        (200, ["data"]),
        (400, None),
    ],
)
def test_fetch_data_page(status_code, expected):
    with requests_mock.Mocker() as m:
        m.get("mock://test.com", json={"data": ["data"]}, status_code=status_code)
        result = fetch_data_page("mock://test.com", {})
        assert result == expected


@pytest.mark.parametrize(
    "pages, expected_len",
    [
        (1, 1),
        (2, 2),
    ],
)
def test_generate_data_pages(pages, expected_len):
    with requests_mock.Mocker() as m:
        m.get(
            URL_BASE,
            [{"json": {"data": ["data"]}, "status_code": 200}] * pages
            + [{"json": {"data": []}, "status_code": 200}],
        )
        result = list(generate_data_pages("01/01/2023"))
        assert len(result) == expected_len
        assert all(isinstance(page, list) for page in result)


@pytest.mark.parametrize(
    "pages, expected_len",
    [
        (1, 1),
        (2, 2),
    ],
)
def test_merge_pages_data(pages, expected_len):
    with requests_mock.Mocker() as m:
        m.get(
            URL_BASE,
            [{"json": {"data": ["data"]}, "status_code": 200}] * pages
            + [{"json": {"data": []}, "status_code": 200}],
        )
        result = merge_pages_data(date(2023, 1, 1))
        assert len(result) == expected_len
