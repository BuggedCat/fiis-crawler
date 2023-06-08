import logging
from dataclasses import dataclass
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.settings import Settings
from scrapy.spiders import Spider

from fiis_crawler.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_SECRET_ACCESS_KEY,
)

logger = logging.getLogger(__name__)


@dataclass
class ExtensionSettings:
    enabled: bool
    log_file: str
    s3_bucket: str

    @staticmethod
    def str_to_bool(value: str | bool) -> bool:
        if isinstance(value, bool):
            return value
        if value.lower() in {"true", "1", "on", "t"}:
            return True
        if value.lower() in {"false", "0", "off", "f"}:
            return False
        raise ValueError(f"Invalid bool value: {value}.")

    @classmethod
    def from_crawler_settings(cls, crawler_settings: Settings):
        s3_log: dict[str, str] = crawler_settings.getdict("S3_LOG", {})  # type: ignore

        if not s3_log:
            raise NotConfigured("S3_LOG settings must be set to use the extension.")

        enabled = cls.str_to_bool(s3_log.get("ENABLED", False))
        s3_bucket = s3_log.get("S3_BUCKET")
        log_file_path = s3_log.get("LOG_FILE_NAME", crawler_settings.get("LOG_FILE", ""))
        if not log_file_path:
            raise NotConfigured("LOG_FILE or LOG_FILE_NAME must be configured.")
        if not s3_bucket:
            raise NotConfigured("S3_BUCKET must be configured.")

        return cls(enabled=enabled, log_file=log_file_path, s3_bucket=s3_bucket)


class S3Logger:
    def __init__(self, extension_settings: ExtensionSettings):
        self.extension_settings = extension_settings

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        extension_settings = ExtensionSettings.from_crawler_settings(
            crawler_settings=crawler.settings
        )

        ext = cls(extension_settings=extension_settings)

        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.log_to_s3, signal=signals.engine_stopped)
        return ext

    def spider_opened(self, spider: Spider):
        logger.info(f"Opened spider {spider.name}")

    def spider_closed(self, spider: Spider):
        logger.info(f"Closed spider {spider.name}")

    @staticmethod
    def s3_client():
        s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=AWS_ENDPOINT_URL,
        )
        return s3_client

    def upload_log_to_s3(self, spider: Spider):
        s3_client = self.s3_client()
        try:
            log_file_name = self.extension_settings.log_file.split("/")[-1]
            s3_path = f"s3://{self.extension_settings.s3_bucket}/{log_file_name}"
            logger.info(
                f"Sending {spider.name} log from '{self.extension_settings.log_file}' to {s3_path}"
            )
            _ = s3_client.upload_file(
                self.extension_settings.log_file,
                self.extension_settings.s3_bucket,
                log_file_name,
            )
            logger.info("Log sent to S3 succesfully.")
            return True
        except ClientError as e:
            logging.error(e)
            logger.error("Error sending log to S3.")
            return False

    def log_to_s3(self, sender: Crawler):
        if not sender.spider:
            raise ValueError

        logger.info(f"Spider {sender.spider.name} engine stopped.")
        self.upload_log_to_s3(sender.spider)
        # logger.info(f"Deleting local log.")
        # logger.info(f"Local log deleted.")
