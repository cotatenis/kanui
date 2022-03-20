# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from google.cloud import storage
from google.oauth2 import service_account
import datetime
import json
from discord_webhook import DiscordWebhook, DiscordEmbed

class DiscordMessenger:
    def __init__(self, webwook_url, bot_name, thumbnail) -> None:
        self.webhook = DiscordWebhook(url=webwook_url)
        self.bot_name = bot_name
        self.thumbnail = thumbnail

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            webwook_url=crawler.settings.get("DISCORD_WEBHOOK_URL"),
            thumbnail=crawler.settings.get("DISCORD_THUMBNAIL_URL"),
            bot_name=crawler.settings.get("BOT_NAME"),
        )

    def open_spider(self, spider):
        embed = DiscordEmbed(
            title=f'BOT {self.bot_name}/{spider.name} has started.')
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_timestamp()
        self.webhook.add_embed(embed=embed)
        _ = self.webhook.execute()

    def close_spider(self, spider):
        self.webhook.remove_embeds()
        stats = spider.crawler.stats.get_stats()
        stats_st = stats.get("start_time")
        if isinstance(stats_st, str):
            stats_st = datetime.datetime.fromisoformat(stats_st)
        finish_time = datetime.datetime.utcnow()
        elapsed_time_seconds = str(finish_time-stats_st)
        item_scraped_count = stats.get("item_scraped_count")
        embed = DiscordEmbed(
            title=f'BOT {self.bot_name}/{spider.name} has ended.')
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_timestamp()
        # add fields to embed
        embed.add_embed_field(name='Elapsed time', value=elapsed_time_seconds)
        embed.add_embed_field(name='Number of products collected', value=item_scraped_count)
        self.webhook.add_embed(embed=embed)
        _ = self.webhook.execute()

class GCSPipeline:
    def __init__(
        self,
        bucket_name,
        bucket_name_stats,
        project_name,
        credentials,
        bot_name,
    ):
        self.bucket_name = bucket_name
        self.bucket_name_stats = bucket_name_stats
        self.project_name = project_name
        self.credentials = credentials
        self.bot_name = bot_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            project_name=crawler.settings.get("GCP_PROJECT_ID"),
            credentials=crawler.settings.get("GCP_CREDENTIALS"),
            bucket_name=crawler.settings.get("GCP_STORAGE"),
            bucket_name_stats=crawler.settings.get("GCP_STORAGE_CRAWLER_STATS"),
            bot_name=crawler.settings.get("BOT_NAME"),
        )

    def open_spider(self, spider):
        self.bucket = self.connect(
            self.project_name, self.bucket_name, self.credentials
        )
        self.bucket_stats = self.connect(
            self.project_name, self.bucket_name_stats, self.credentials
        )
    def close_spider(self, spider):
        year = datetime.datetime.now().year
        day = datetime.datetime.now().isoformat().split("T")[0]
        timestamp_fmt = datetime.datetime.now().isoformat().replace("-", "").replace(":", "").split(".")[0]
        stats = spider.crawler.stats.get_stats()
        stats['spider'] = spider.name
        stats_st = stats.get("start_time").isoformat()
        stats['start_time'] = stats_st
        stats['finish_time'] = datetime.datetime.utcnow().isoformat()
        filename = f"{year}/{day}/{self.bot_name}/{timestamp_fmt}_{spider.name}_stats.json"
        blob = self.bucket_stats.blob(filename)
        blob.upload_from_string(json.dumps(stats), content_type="application/json")

    def connect(self, project_name, bucket_name, credentials):
        credentials_obj = service_account.Credentials.from_service_account_file(
            credentials
        )
        client = storage.Client(credentials=credentials_obj, project=project_name)
        return client.get_bucket(bucket_name)

    def upload(self, content: str, filename: str) -> str:
        blob = self.bucket.blob(filename)
        blob.upload_from_string(content, content_type="application/json")
        return None

    def process_item(self, item, spider):
        item_name = type(item).__name__
        raw_item = ItemAdapter(item)
        timestamp_fmt = (
            raw_item.get("timestamp", "")
            .replace("-", "")
            .replace(":", "")
            .split(".")[0]
        )
        year = datetime.datetime.now().year
        day = datetime.datetime.now().isoformat().split("T")[0]
        if item_name == "KanuiItem":
            filename = f"{year}/{day}/{self.bot_name}/{timestamp_fmt}_{spider.name}_{raw_item.get('spider_version', '')}_{item_name}_{raw_item.get('sku')}.json"
            self.upload(content=json.dumps(dict(raw_item)), filename=filename)
        elif item_name == "KanuiStockItem":
            filename = f"{year}/{day}/{self.bot_name}/{timestamp_fmt}_{spider.name}_{raw_item.get('spider_version', '')}_{item_name}_{raw_item.get('base_sku')}.json"
            self.upload(content=json.dumps(dict(raw_item)), filename=filename)
        return None