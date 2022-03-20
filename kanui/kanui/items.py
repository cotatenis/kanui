# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags, replace_escape_chars, strip_html5_whitespace
from scrapy.item import Item
from dataclasses import dataclass

def cleaning_price(text):
    return text.replace("R$", "")

def cleaning_html_text(text):
    raw = text.split(" ")
    text = [d for d in raw if d!=""]
    return text


def cleaning_description(text):
    return text.replace("\u00ae", " ").replace("\xa0", " ")


class KanuiItem(Item):
    brand = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, replace_escape_chars, strip_html5_whitespace
        ),
        output_processor=TakeFirst(),
    )
    product = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, replace_escape_chars, strip_html5_whitespace
        ),
        output_processor=TakeFirst(),
    )
    seller_name = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, replace_escape_chars, strip_html5_whitespace
        ),
        output_processor=TakeFirst(),
    )
    seller_url = scrapy.Field(
        input_processor=MapCompose(replace_escape_chars, strip_html5_whitespace),
        output_processor=TakeFirst(),
    )
    price = scrapy.Field(
        input_processor=MapCompose(
            replace_escape_chars, strip_html5_whitespace, cleaning_price
        ),
        output_processor=TakeFirst(),
    )
    url = scrapy.Field(
        input_processor=MapCompose(strip_html5_whitespace), output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(
            remove_tags,
            replace_escape_chars,
            cleaning_description,
            strip_html5_whitespace,
        )
    )
    info = scrapy.Field(input_processor=MapCompose(
            remove_tags,
            replace_escape_chars,
            cleaning_description,
            strip_html5_whitespace,
            cleaning_html_text))
    sku = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, replace_escape_chars, strip_html5_whitespace
        ),
        output_processor=TakeFirst(),
    )
    in_stock = scrapy.Field(output_processor=TakeFirst())
    timestamp = scrapy.Field()
    spider = scrapy.Field()
    spider_version = scrapy.Field(output_processor=TakeFirst())


@dataclass
class KanuiStockItem:
    base_sku: str
    spider: str
    spider_version: str
    timestamp: str
    sizes: list
    colors: list
    specialPrice: str
    price: str
    installments: dict
    campaigns: list