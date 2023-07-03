from datetime import date, datetime, timedelta

Date = date | datetime


def date_parser(value: str | date | datetime) -> date | datetime:
    if isinstance(value, (date, datetime)):
        return value
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y%m%d",
        "%d%m%Y",
        "%m%d%Y",
    ]

    for date_format in formats:
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            pass

    raise ValueError(f"Time '{value}' is not in a recognized format")


def date_range(start_date: date, end_date: date, include_weekends: bool = True):
    delta = timedelta(days=1)

    while start_date <= end_date:
        if include_weekends or start_date.weekday() < 5:
            yield start_date
        print(start_date, start_date.weekday())
        start_date += delta
