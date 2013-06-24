from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider
from scrapy import log

from cpi_scrapers.items import ProductItem

import re
import json

class DealsDirectSpider(CrawlSpider):

    name = "dealsdirect"
    store_url = "http://www.dealsdirect.com.au"
    start_urls = [
        store_url,
    ]

    xpaths = {
        # {{{
        'parse_categories': '//div[@id="mlc"]//li//a/@href',

        'parse_category_products': '//div[@class="prod"]//h2[@itemprop]/a/@href',
        'parse_category_next': '//div[@class="pag "]/ul/li[@class="textnav"]/a[@rel="next"]/@href',

        'parse_product_product_name': '//span[@itemprop="name"]/text()',
        'parse_product_product_number_deal': '//div[@id="pd_deal"]//input[@name="pID"]/@value',
        'parse_product_product_number_img': '//div[@id="pd_img"]//input[@name="pID"]/@value',
        'parse_product_product_number_img_add2wl': '//span[@class="add2wl"]/@onclick',
        'parse_product_description': '//div[@id="pd_desc"]//text()',
        'parse_product_categories': '//div[@id="pd_bcr"]/ul//li/*/text()',
        'parse_product_image_url': '//img[@id="pd_imgtag"]/@src',
        'parse_product_availability': '//div[@id="pd_deal"]//p[@class="stock"]/strong/text()',
        'parse_product_sale_price': '//span[@itemprop="price"]//text()',
        'parse_product_on_sale_save': '//div[@class="midcart_widget"]//li[@class="save"]',
        'parse_product_on_sale_img': '//div[@id="pd_img"]//div[contains(@class, "nl-promo")]',
 
        # }}}
    }

    AVAIL_CHOICES = {
        # {{{
        'discontinued': ProductItem.AVAIL_DC,
        'instock': ProductItem.AVAIL_IS,
        'instoreonly': ProductItem.AVAIL_ISO,
        'outofstock': ProductItem.AVAIL_OOS,
        'soldout': ProductItem.AVAIL_OOS,
        'availabletoorder': ProductItem.AVAIL_ATO,
        'preorder': ProductItem.AVAIL_PO,
        # }}}
    }

    # Shipping Cost URL, string format param is pID
    SC_URL = u'http://www.dealsdirect.com.au/goldCalculateShipping.php?gold_postcode=2000&pID=%s'

    def extract_xpath(self, hxs, name_xpath):
        xpath = self.xpaths[name_xpath]
        return hxs.select(xpath).extract()

    def parse(self, response):
        ''' ''' # {{{
        hxs = HtmlXPathSelector(response)
        categories = hxs.select(self.xpaths['parse_categories']).extract()
        for category_page in categories:
            category_page = self.store_url + category_page
            yield Request(category_page, callback=self.parse_category, dont_filter=True)
        # }}}

    def parse_category(self, response):
        ''' ''' # {{{
        hxs = HtmlXPathSelector(response)
        products = hxs.select(self.xpaths['parse_category_products']).extract()
        for product in products:
            product_page = self.store_url + product
            yield Request(product_page, callback = self.parse_product)

        next_page = hxs.select(self.xpaths['parse_category_next']).extract()
        if next_page:
            next_page = self.store_url + str(next_page[0])
            yield Request(next_page, callback=self.parse_category, dont_filter=True)
        # }}}

    def parse_product(self, response):
        ''' ''' # {{{ 
        #self.log(response.url, level=log.INFO)

        if response.url == self.store_url + '/':
            return

        hxs = HtmlXPathSelector(response)
        item = ProductItem()

        # Source
        item['source'] = self.store_url

        # Product Name
        # {{{
        tmp = self.extract_xpath(hxs, 'parse_product_product_name')
        if len(tmp) != 1:
            raise ValueError('No Product Name')
        item['product_name'] = tmp[0]
        # }}}

        # Product Number
        # {{{
        tmp = self.extract_xpath(hxs, 'parse_product_product_number_deal') # In Stock
        if len(tmp) == 0:
            tmp = self.extract_xpath(hxs, 'parse_product_product_number_img') # Out of Stock
            if len(tmp) == 0:
                tmp = self.extract_xpath(hxs, 'parse_product_product_number_img_add2wl') # Out of Stock and No Image
                if len(tmp) == 0:
                    raise ValueError('No Product Number')
                re_add2wl = re.compile('pid=(\d+)')
                ms = re_add2wl.search(tmp[0])
                tmp = ms.groups()
                if len(tmp) == 0:
                    raise ValueError('No Product Number')

        item['product_number'] = tmp[0]
        # }}}

        # Description
        # {{{
        tmp = self.extract_xpath(hxs, 'parse_product_description') 
        if len(tmp) is 0:
            raise ValueError('No Description')
        else:    
            item['description'] = '\n'.join(map(lambda s: s.strip(), tmp)).strip()
        # }}}

        # Categroy Name
        # {{{
        tmp = self.extract_xpath(hxs, 'parse_product_categories')
        if len(tmp) <= 0:
            raise ValueError('No Categories')

        cg_paths = []
        cg_path = []

        for c in tmp:
            c = c.strip()
            if c == '':
                continue
            elif c == 'Home':
                cg_path = ProductItem.CG_PATH_SEP.join(cg_path)
                if cg_path != '':
                    cg_paths.append(cg_path)
                cg_path = ['Home']
            else:
                cg_path.append(c)

        cg_paths.append(ProductItem.CG_PATH_SEP.join(cg_path))
        item['category_name'] = ProductItem.CG_PATHS_SEP.join(cg_paths)
        # }}}

        # Product URL
        item['product_url'] = response.url

        # Image URL
        tmp = self.extract_xpath(hxs, 'parse_product_image_url')
        if len(tmp) is 0:
            raise ValueError('No Image URL')
        else:
            item['image_url'] = self.extract_xpath(hxs, 'parse_product_image_url')[0]

        # Product Condition
        item['product_condition'] = ProductItem.PC_NEW

        # Availability
        tmp = self.extract_xpath(hxs, 'parse_product_availability')
        if len(tmp) != 1:
            raise ValueError('No Availability')
        else:
            tmp = self.AVAIL_CHOICES.get(re.sub('\s+', '', tmp[0].lower()))
            if not tmp: 
                raise ValueError('No such Availability')
            item['availability'] = tmp
        
        # Sale Price 
        tmp = self.extract_xpath(hxs, 'parse_product_sale_price')
        tmp = re.sub('[$|\s]', '', ''.join(tmp))
        item['sale_price'] = float(tmp)

        # On Sale 
        item['on_sale'] = 0
        if len(self.extract_xpath(hxs, 'parse_product_on_sale_img')) > 0 or len(self.extract_xpath(hxs, 'parse_product_on_sale_save')) > 0:
            item['on_sale'] = 1

        # Currency
        item['currency'] = 'AUD'

        # Manufacturer
        item['manufacturer'] = ''

        ## Optional Field
        # {{{
        #item['gtin'] = None
        #item['mpn'] = None
        #item['product_sku'] = None
        #item['product_spec'] = None
        #item['cost_price'] = None
        #item['num_reviews'] = None
        #item['avg_reviews_points'] = None
        #item['keywords'] = None
        # }}}
        
        # Shipping Cost 
        # Generate a Request to get the Shipping Cost
        request = Request(self.SC_URL % (item['product_number']), callback=self.parse_shipping_cost)
        request.meta['item'] = item

        return request
    
        # }}}

    def parse_shipping_cost(self, response):
        ''' ''' # {{{

        item = response.meta['item']
        sc_list = json.loads(response.body)

        item['shipping_cost'] = 0 if len(sc_list) < 1 else float(sc_list[0])

        #print item

        return item

        # }}}
