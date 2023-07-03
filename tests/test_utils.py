from datetime import date, datetime

import pytest

from fiis_scraper.utils import date_parser, date_range


@pytest.mark.parametrize(
    "input_date,expected_date",
    [
        ("2023-06-30", datetime(2023, 6, 30)),
        ("30/06/2023", datetime(2023, 6, 30)),
        ("06-30-2023", datetime(2023, 6, 30)),
        (date(2023, 6, 30), date(2023, 6, 30)),
        (datetime(2023, 6, 30, 15, 30), datetime(2023, 6, 30, 15, 30)),
    ],
)
def test_date_parser_with_strings(input_date, expected_date):
    assert date_parser(input_date) == expected_date


@pytest.mark.parametrize(
    "unrecognized_date_string",
    [
        "2023.06.30",
        "30.06.2023",
        "06.30.2023",
    ],
)
def test_date_parser_with_unrecognized_format(unrecognized_date_string):
    with pytest.raises(ValueError) as e:
        date_parser(unrecognized_date_string)
    assert str(e.value) == f"Time '{unrecognized_date_string}' is not in a recognized format"


@pytest.mark.parametrize(
    "start_date, end_date, include_weekends, expected",
    [
        (date(2023, 1, 1), date(2023, 1, 7), True, [date(2023, 1, i) for i in range(1, 8)]),
        (
            date(2023, 1, 1),
            date(2023, 1, 7),
            False,
            [
                date(2023, 1, 2),
                date(2023, 1, 3),
                date(2023, 1, 4),
                date(2023, 1, 5),
                date(2023, 1, 6),
            ],
        ),
    ],
)
def test_date_range(start_date, end_date, include_weekends, expected):
    assert list(date_range(start_date, end_date, include_weekends)) == expected
