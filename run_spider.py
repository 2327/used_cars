from scraper.spiders.auto_spider import CarSpider
from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess


try:

    settings = Settings()

    settings.setmodule('scraper.settings')

    process = CrawlerProcess(settings=settings)

    process.crawl(CarSpider)

    process.start()

except Exception as e:
    print(f'Closed by {e}')
    CarSpider.close(reason=e)
