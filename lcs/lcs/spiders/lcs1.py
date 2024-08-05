import pandas as pd
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

def decode_cloudflare_email(encoded_email):
    r = int(encoded_email[:2], 16)
    email = ''.join([chr(int(encoded_email[i:i+2], 16) ^ r) for i in range(2, len(encoded_email), 2)])
    return email


class Lcs1Spider(CrawlSpider):
    name = "lcs1"
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    allowed_domains = ["thelifecoachschool.com"]
    start_urls = ["https://thelifecoachschool.com/directory/?pg=1"]

    rules = [Rule(LinkExtractor(restrict_xpaths='//div[@class="cmed_tiles_view_container"]//div[@class="part1"]/a'), callback="parse_item", follow=True),
             Rule(LinkExtractor(restrict_xpaths='//a[@class="next page-numbers cmed-button cmed-button"]'))]

    def parse_item(self, response):
        item = {}
        item['url'] = response.url
        full_name_block = response.xpath('//div[@class="cmed-title"]/text()').get().strip()
        full_name_block = full_name_block.split(',')[0]
        # full_name_block = full_name_block.replace('MD', '').strip().replace('Dr', '').strip().replace('Dr.', '').strip().split()
        full_name_block = full_name_block.replace('MD', '').replace('Dr', '').replace('Dr.','').lstrip('.').strip().split()
        if len(full_name_block) > 1:
            if '. ' in full_name_block:
                item['first name'] = ' '.join(full_name_block[:-1])
                item['last_name'] = full_name_block[-1]
            else:
                item['first name'] = full_name_block[0]
                item['last_name'] = ' '.join(full_name_block[1:])
        else:
            item['first name'] = full_name_block[0]
            item['last_name'] = '-'

        item['type of coach'] = ''.join([x.replace(':', '').strip() for x in response.xpath('//div[@class="cmed_position"]//span/text()').getall()])

        item['phone'] = response.xpath('//div[@class="cmed-info-box-phone"]/text()').get()

        contact_block = response.xpath('//aside[@class="expert-aside"]//div[@class="cmed-info-box" and @id="contact-box"]/ul[@class="list-unstyled"]/li')

        try:
            coded_email = contact_block.xpath('./a[contains(text(), "Contact")]/@href').get().split('#')[-1]
            item['email'] = decode_cloudflare_email(coded_email)
        except:
            item['email'] = '-'

        item['facebook'] = contact_block.xpath('./a[@class="cmed-info-box-link" and contains(@href, "facebook.com")]/@href').get()
        item['instagram'] = contact_block.xpath('./a[@class="cmed-info-box-link" and contains(@href, "instagram.com")]/@href').get()
        item['website'] = contact_block.xpath('./a[contains(text(), "Website")]/@href').get()
        return item

df = pd.read_json('/home/igor/Desktop/upwork_projects/everjoy111/lcs/3.json')
df.to_excel('res3.xlsx', index=False)