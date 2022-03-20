from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from kanui.items import KanuiItem, KanuiStockItem
import datetime
from scrapy.loader import ItemLoader
from scrapy import Request
class KanuiAdidasSpider(CrawlSpider):
    name = "kanui-adidas"
    version = "0-1-1"
    allowed_domains = ["www.kanui.com.br"]
    start_urls = [
        "https://www.kanui.com.br/calcados-masculinos/tenis/adidas?segment=masculino",
        "https://www.kanui.com.br/calcados-masculinos/tenis/adidas--adidas-combat-sports/",
    ]
    product_details = LinkExtractor(restrict_xpaths="//div[@class='product-box']/div/a")
    pagination = LinkExtractor(restrict_xpaths=("//li[normalize-space(@class) = 'page']", "//li[normalize-space(@class) = 'page next']"))
    rules = [Rule(product_details, callback='parse_products'), Rule(pagination, follow=True)]

    def parse_products(self, response):
        if response.url in self.start_urls:
            return None
        else:
            product_container = response.xpath("//div[normalize-space(@class) = 'container product-page']")
            i = ItemLoader(item=KanuiItem(), selector=product_container)
            is_product_in_stock = response.xpath("//div[@class='stock-available-message']").get()
            if is_product_in_stock == 'Não disponível em estoque':
                i.add_value("url", response.url)
                i.add_xpath("brand", "//a[@itemprop='brand']/@title")
                i.add_xpath("product", "//h1[@class='product-name']")
                i.add_xpath("price", "//span[@class='catalog-detail-price-value']/@content")
                i.add_xpath("sku", "//td[@itemprop='sku']")
                i.add_value("spider_version", self.version)
                i.add_value("spider", self.name)
                yield i.load_item()
            else:
                i.add_value("url", response.url)
                i.add_xpath("brand", "//a[@itemprop='brand']/@title")
                i.add_xpath("product", "//h1[@class='product-name']")
                i.add_xpath("price", "//span[@class='catalog-detail-price-value']/@content")
                i.add_xpath("sku", "//td[@itemprop='sku']")                
                i.add_xpath("info", "//div[normalize-space(@class) = 'box-informations']")
                i.add_value("in_stock", True)
                i.add_value("spider_version", self.version)
                i.add_value("spider", self.name)
                i.add_xpath("description", "//p[@class='product-information-description']")
                yield i.load_item()
                sku = response.xpath("//td[@itemprop='sku']/text()").get()
                if sku:
                    stock_request_url = (
                        f"https://www.kanui.com.br/catalog/detailJson?sku={sku}"
                    )
                    headers = {
                        "authority": "www.kanui.com.br",
                        "pragma": "no-cache",
                        "cache-control": "no-cache",
                        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
                        "accept": "*/*",
                        "x-requested-with": "XMLHttpRequest",
                        "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
                        "sec-fetch-site": "same-origin",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-dest": "empty",
                        "referer": response.url,
                        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
                    }
                    yield Request(
                        url=stock_request_url,
                        headers=headers,
                        method="GET",
                        dont_filter=True,
                        callback=self.parse_stock_info,
                        cb_kwargs={"sku": sku},
                    )

    def parse_stock_info(self, response, sku):
        raw_stock_data = response.json()
        raw_stock_data["base_sku"] = sku
        raw_stock_data["spider"] = self.name
        raw_stock_data["spider_version"] = self.version
        raw_stock_data["timestamp"] = datetime.datetime.now().isoformat()
        stock_data = KanuiStockItem(**raw_stock_data)
        itemproc = self.crawler.engine.scraper.itemproc
        itemproc.process_item(stock_data, self)