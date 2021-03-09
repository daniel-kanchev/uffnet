from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from uffnet.items import Article
import scrapy


class UffnetSpider(scrapy.Spider):
    name = 'uffnet'
    start_urls = ['https://www.uff.net/actualites']

    def parse(self, response):
        links = response.xpath('//div[@class="rowContent marginBottom paragraph paragraph--type--mod-005 '
                               'paragraph--view-mode--default"]//div[@role="article"]//a[@class="ctaBloc"]'
                               '/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="bcc-007 mainTitle"]/text()[last()]').get() or \
                response.xpath('//h1/span/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="bcc-006 wysiwygContent"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
