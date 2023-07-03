import argparse
from datetime import date, datetime
from typing import Any

from fiis_scraper.aws.utils import put_to_s3, s3_client_connection
from fiis_scraper.documentos.crawl import merge_pages_data
from fiis_scraper.utils import date_parser, date_range


def parse_arguments() -> argparse.Namespace:
    """
    Analisa os argumentos da linha de comando.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--reference-date",
        type=date_parser,
        help="The reference date of the documents to be fetched",
    )
    parser.add_argument(
        "-s",
        "--start-date",
        type=date_parser,
        help="The start date of the documents to be fetched",
    )
    parser.add_argument(
        "-e",
        "--end-date",
        type=date_parser,
        help="The end date of the documents to be fetched",
    )
    return parser.parse_args()


def process_and_upload_data(
    reference_date: date | datetime,
    bucket: str,
    s3_client: Any,
):
    """
    Processa os dados para uma data específica e faz o upload para o S3.
    """
    data = merge_pages_data(reference_date)
    file_date = reference_date.strftime("%Y-%m-%d")
    s3_key = f"reference_date={file_date}/documents.json"
    put_to_s3(bucket, s3_key, data, s3_client)


def main():
    """
    Função principal.
    """
    args = parse_arguments()
    bucket = "bronze"

    with s3_client_connection() as s3_client:
        if args.reference_date:
            process_and_upload_data(args.reference_date, bucket, s3_client)

        if args.start_date and args.end_date:
            for reference_date in date_range(args.start_date, args.end_date):
                process_and_upload_data(reference_date, bucket, s3_client)


if __name__ == "__main__":
    main()
