from scraper.spiders.auto_spider import CarSpider
from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

settings = Settings()

settings.setmodule('scraper.settings')

try:
    process = CrawlerProcess(settings=settings)

    process.crawl(CarSpider)

    process.start()

except Exception as e:
    print(f'Closed by {e}')
    CarSpider.close(reason=e)
