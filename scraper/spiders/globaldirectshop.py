# pylint: skip-file
from scrapy.contrib.spiders import CSVFeedSpider
from scrapy.exceptions import CloseSpider
from scrapy import log

from scraper.items import ProductItem

import re

AVAIL_CHOICES = {
    # {{{
    'discontinued': ProductItem.AVAIL_DC,
    'instock': ProductItem.AVAIL_IS,
    'instoreonly': ProductItem.AVAIL_ISO,
    'outofstock': ProductItem.AVAIL_OOS,
    'soldout': ProductItem.AVAIL_OOS,
    'availabletoorder': ProductItem.AVAIL_ATO,
    'preorder': ProductItem.AVAIL_PO,
} # }}}

def convert_availability(v):
    # {{{
    tmp = AVAIL_CHOICES.get(re.sub('\s+', '', v.lower()))
    if not tmp:
        raise ValueError('No such Availability: %s' % v)
    return tmp
    # }}}


class GlobaldirectshopSpider(CSVFeedSpider):
    name = 'globaldirectshop'
    start_urls = ['http://cpi-feeds.appspot.com/store/6323566249246720/', ]

    source = 'http://www.globaldirectshop.com.au/'

    headers = ['pid', 'sku', 'category', 'name', 'produrl', 'availability', 'price', 'picurl']
    delimiter = ','

    # "pid","sku","category","name","produrl","availability","price","picurl"
    # "114","GR-9403-TUNBDSP","iPod Accessories","Earphones - Griffin TuneBuds: Pink","http://www.globaldirectshop.com.au/product_info.php?products_id=114","In Stock","36.90","http://www.globaldirectshop.com.au/images/114_M.gif"
    fields = (
        ('pid', 'product_number', None),
        ('sku', 'product_sku', None),
        ('category', 'category_name', None),
        ('name', 'product_name', None),
        ('produrl', 'product_url', None),
        ('availability', 'availability', convert_availability),
        ('price', 'sale_price', float),
        ('picurl', 'image_url', None),
    )

    # Do any adaptations you need here
    def adapt_response(self, response):
        header = ','.join('"%s"' % field for field in self.headers)
        body = response.body

        if not body.startswith(header):
            raise CloseSpider('response body dose not start by header\n%s\n%s' % (body[len(header)+10], header))

        response = response.replace(body=body[len(header):].strip())
        return response

    def parse_row(self, response, row):
        # {{{
        item = ProductItem()

        for field in ProductItem.VALIDATION_REQUIRED:
            item[field] = ''

        item['source'] = self.source
        item['product_condition'] = ProductItem.PC_NEW
        item['on_sale'] = 0
        item['currency'] = 'AUD'
        item['shipping_cost'] = -1

        for field in self.fields:
            func = field[2]
            item[field[1]] = func(row[field[0]]) if func else row[field[0]]

        return item
        # }}}

