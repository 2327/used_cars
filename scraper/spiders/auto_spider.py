import re
import time
# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy import signals

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..items import CarsScraperItem
# from .scraper.items import CarsScraperItem


class CarSpider(Spider):

    name = "used_cars_spider"

    allowed_domains = ['auto.ru']
    start_urls = [
        'https://auto.ru/'
    ]

    def __init__(self):

        super().__init__()

        # Настройки для запуска движка браузера без открытия окна
        self.firefox_options = Options()
        self.firefox_options.add_argument("--headless")

        # self.driver = webdriver.Firefox()

        self.driver = webdriver.Firefox(options=self.firefox_options)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CarSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # Закрыте драйвера Selenium по окончании работы
        print('Closing spider...')
        self.driver.quit()

    def only_digit(self, item):
        # Очистка полей "пробег" и "цена" от лишних символов
        return re.sub(r'\s|\xa0|\D', '', item)

    def parse(self, response):

        print("Log Enabled: %s" % self.settings.getbool('LOG_ENABLED'))

        # получение страницы движком
        self.driver.get(response.url)

        # серия кликов для настройки отображения по всем регионам
        open_region_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".GeoSelect__title-shrinker"))
        )
        open_region_select.click()

        clear_region = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".GeoSelectPopupRegion__clear"))
        )
        clear_region.click()

        clear_region_save = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".RichInput__popup .Button_size_xl"))
        )
        clear_region_save.click()

        # открытие полного списка марок автомобилей
        open_full_list = self.driver.find_element_by_css_selector('.IndexMarks__show-all')

        try:
            open_full_list.click()
            time.sleep(5)

            # передача полученной движком страницы в селектор Scrapy
            selector = Selector(text=self.driver.page_source.encode('utf-8'))

            for item in selector.css('.IndexMarks__marks-with-counts .IndexMarks__item'):
                # print(item.css('a::attr(href)').extract_first(), item.css('.IndexMarks__item-name::text').extract_first())

                yield response.follow(item.css('a::attr(href)').extract_first(), callback=self.parse_brand)

        except Exception as exc:
            print("*" * 50, exc, "*" * 50)

    def parse_brand(self, response):

        # debug
        print('='*50, response.url)

        self.driver.get(response.url)

        try:
            # Клик по кнопке открытия полного списка моделей
            open_full_brand_list = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ListingPopularMMM-module__container span.Link'))
            )
            open_full_brand_list.click()

        except Exception:
            # Если такой кнопки нет, ничего не делать
            pass

        finally:
            # Передача получившейся страницы в Scrapy
            selector = Selector(text=self.driver.page_source.encode('utf-8'))

            for item in selector.css('.ListingPopularMMM-module__item'):
                # print(item.css('a::attr(href)').extract_first(), item.css('a::text').extract_first())

                yield response.follow(item.css('a::attr(href)').extract_first(), callback=self.parse_model)

    def parse_model(self, response):

        # debug
        print('#'*50, response.url)

        item = CarsScraperItem()

        # Марку и модель берем из "хлебных крошек", так как в описании автомобиля
        # они вписаны в одно поле, и разделить их сложно
        brand = response.css('.ListingCarsHead__breadcrumbs a::text').extract_first()
        model = response.css('.ListingCarsHead__breadcrumbs a:nth-child(2)::text').extract_first()

        for offer in response.css('.ListingCars-module__list .ListingItem-module__main'):

            # debug
            print('+')

            price = offer.css('div.ListingItemPrice-module__content::text').extract_first()
            year = offer.css('div.ListingItem-module__year::text').extract_first()
            kmage = offer.css('div.ListingItem-module__kmAge::text').extract_first()

            item['brand'] = brand
            item['model'] = model
            item['year'] = year
            item['kmage'] = self.only_digit(kmage)
            item['price'] = self.only_digit(price)

            yield item

        next_page = response.css('a.ListingPagination-module__next::attr(href)').extract_first()
        if next_page is not None:
            print('====================================================')
            yield response.follow(next_page, callback=self.parse_model)


if __name__ == '__main__':

    settings = Settings()

    settings.setmodule('used_cars.scraper.settings')

    try:
        process = CrawlerProcess(settings=settings)

        process.crawl(CarSpider)

        process.start()

    except Exception as e:
        print(f'Closed by {e}')
        CarSpider.close(reason=e)
