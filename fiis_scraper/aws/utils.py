import json
from contextlib import contextmanager
from typing import Any

import boto3

from fiis_scraper.settings import environment


def put_to_s3(
    bucket: str,
    key: str,
    data: dict[str, Any] | list[dict[str, Any]],
    s3_client,
) -> None:
    """
    Coloca os dados no bucket S3 especificado com a chave fornecida.

    Args:
        bucket (str): O nome do bucket S3.
        key (str): A chave sob a qual os dados serão armazenados.
        data (dict): Os dados a serem armazenados.
    """
    try:
        json_data = json.dumps(data, ensure_ascii=False)
        s3_client.put_object(
            Body=json_data,
            Bucket=bucket,
            Key=key,
        )
        print(f"Data successfully put to S3 under the key {key} in the bucket {bucket}.")
    except Exception as e:
        raise e


@contextmanager
def s3_client_connection():
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=environment.AWS_ACCESS_KEY_ID.get_secret_value(),
            aws_secret_access_key=environment.AWS_SECRET_ACCESS_KEY.get_secret_value(),
            endpoint_url=environment.AWS_ENDPOINT.unicode_string(),
        )
        yield s3_client
    finally:
        s3_client.close()
