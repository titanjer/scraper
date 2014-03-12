from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider
from scrapy import log

from scraper.items import ProductItem

import re
import json
import lxml.html
import copy


class OzbinocularsSpider(CrawlSpider):

    name = "ozbinoculars"
    store_url = "http://www.ozbinoculars.com.au"
    start_urls = [
        'http://www.ozbinoculars.com.au/catalog/seo_sitemap/product/?p=1',
    ]

    xpaths = {
        # {{{
        'parse_sitemap_links': '//ul[@class="sitemap"]/li/a/@href',

        'parse_next_page':
        '//a[contains(@class,"next") and contains(@title,"Next")]/@href',

        'parse_product_table': '//table[@id="super-product-table"]',
        'parse_product_table_product_link':
        '//td[@class="table_column_dash"]/a/@href',

        'parse_product_super':
        '//select[contains(@class,"super-attribute-select")]',

        'parse_product_product_name':
        '//h1[@itemprop="name"]/text()',
        'parse_product_number':
        '//form[@id="product_addtocart_form"]/@action',
        'parse_product_sku':
        '//p[@itemprop="productID"]/text()',
        'parse_product_description':
        '//div[@class="std"]',
        'parse_product_categories':
        '//div[@id="pd_bcr"]/ul//li/*/text()',
        'parse_product_image_url':
        '//meta[@property="og:image"]/@content',
        'parse_product_availability':
        '//div[@class="cart_box_availability in-stock"]/text()',
        'parse_product_availability_oos':
        '//div[@class="out-of-stock-notice"]',
        'parse_product_sale_price':
        '//span[@class="price"]/text()',
        'parse_product_on_sale_save':
        '//span[@class="price-label" and contains(text(),"Sale Price")]',
        'parse_product_manufacturer':
        '//th[contains(text(),"Manufacturer")]//'
        'following-sibling::*[1]/text()',
        'product_ratings_box':
        '//div[@class="ratings"]',
        'product_rating_value':
        '//div[@itemprop="ratingValue"]/text()',
        'product_num_reviews':
        '//span[@itemprop="ratingCount"]/text()',
        # }}}
    }

    AVAIL_CHOICES = {
        # {{{
        'instock': ProductItem.AVAIL_IS,
        'available': ProductItem.AVAIL_ATO,
        'backorder': ProductItem.AVAIL_ATO,
        # }}}
    }

    # Shipping Cost URL, string format param is pID
    SC_URL = u'http://www.dealsdirect.com.au/goldCalculateShipping.php' \
             u'?gold_postcode=2000&pID=%s'

    def extract_xpath(self, hxs, name_xpath):
        xpath = self.xpaths[name_xpath]
        return hxs.select(xpath).extract()

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        links = self.extract_xpath(hxs, 'parse_sitemap_links')
        for link in links:
            yield Request(link, callback=self.parse_product)

        next_page = self.extract_xpath(hxs, 'parse_next_page')
        if len(next_page):
            yield Request(next_page[0], callback=self.parse)

    def make_shipping_cost_request(self, item, url):
        # Shipping Cost
        # Generate a POST Request to get the Shipping Cost
        _ = 'http://www.ozbinoculars.com.au/ajaxshippingcalculator/index/' \
            'post/?postcode=2000&productId=%s' % item['product_number']
        request = Request(_, method='POST',
                          callback=self.parse_shipping_cost,
                          dont_filter=True)
        request.meta['item'] = item
        request.meta['shipping_for'] = url
        return request

    def parse_product(self, response):
        ''' '''  # {{{
        #self.log(response.url, level=log.INFO)

        if response.url == self.store_url + '/':
            return

        hxs = HtmlXPathSelector(response)

        _ = self.extract_xpath(hxs, 'parse_product_table')
        if len(_):
            # several products in table, parse and yield requests for each
            _ = self.extract_xpath(hxs, 'parse_product_table_product_link')
            if len(_):
                for link in _:
                    yield Request(link, callback=self.parse_product)
                return

        item = ProductItem()

        # Source
        item['source'] = self.store_url

        # Product Number
        # {{{
        _ = self.extract_xpath(hxs, 'parse_product_number')
        if not len(_):
            raise ValueError('No Product Number')
        item['product_number'] = _[0].split('/')[-2]
        # }}}

        # Product Name
        # {{{
        _ = self.extract_xpath(hxs, 'parse_product_product_name')
        if not len(_):
            raise ValueError('No Product Name')
        item['product_name'] = _[0]
        # }}}

        # Description
        # {{{
        _ = self.extract_xpath(hxs, 'parse_product_description')
        if not len(_):
            raise ValueError('No Description')
        document = lxml.html.document_fromstring(_[0])
        item['description'] = document.text_content().strip()
        # }}}

        # Category Name
        # {{{
        parts = hxs.select('//div[@class="breadcrumbs"]/ul/li/*').extract()
        # strip html tags from breadcrumbs
        breadcrumbs = [re.sub(r'<[^>]*?>', ' ', part).strip()
                       for part in parts]
        cat_items = [part for part in breadcrumbs if part != u'&gt;']
        categories = ProductItem.CG_PATH_SEP.join(cat_items)
        # if not len(categories) or not len(response.meta['categories']):
        #     raise ValueError('No Categories')
        if not len(categories):
            raise ValueError('No Categories')
        # item['category_name'] = response.meta['categories'] +\
        #     ProductItem.CG_PATHS_SEP + categories
        item['category_name'] = categories
        # }}}

        # Product URL
        item['product_url'] = response.url

        # Image URL
        _ = self.extract_xpath(hxs, 'parse_product_image_url')
        if not len(_):
            raise ValueError('No Image URL')
        item['image_url'] =\
            self.extract_xpath(hxs, 'parse_product_image_url')[0]

        # Product Condition
        item['product_condition'] = ProductItem.PC_NEW

        # Availability
        _ = self.extract_xpath(hxs, 'parse_product_availability')
        if not len(_):
            _ = self.extract_xpath(hxs, 'parse_product_availability_oos')
            if not len(_):
                raise ValueError('Wrong Availability')
            else:
                item['availability'] = ProductItem.AVAIL_OOS
                item['shipping_cost'] = -1
        else:
            tmp = self.AVAIL_CHOICES.get(re.sub('\s+', '', _[0].strip().lower()))
            if not tmp:
                raise ValueError(u'No such Availability %s' % re.sub('\s+', '', _[0].strip().lower()))
            item['availability'] = tmp

        # Sale Price
        _ = self.extract_xpath(hxs, 'parse_product_sale_price')
        if not len(_):
            raise ValueError('No Sale Price')
        _ = re.sub('[$|\s]', '', _[0].strip())
        item['sale_price'] = float(_.replace(',', ''))

        # On Sale
        item['on_sale'] =\
            int(len(self.extract_xpath(hxs,
                                       'parse_product_on_sale_save')) > 0)
        # Currency
        item['currency'] = 'AUD'

        # Manufacturer
        _ = self.extract_xpath(hxs, 'parse_product_manufacturer')
        if not len(_):
            raise ValueError('No Manufacturer')
        item['manufacturer'] = _[0].strip()

        # Product SKU
        # {{{
        _ = self.extract_xpath(hxs, 'parse_product_sku')
        if len(_):
            item['product_sku'] = _[0].split('#')[1].strip()
        # }}}

        # Ratings
        _ = self.extract_xpath(hxs, 'product_ratings_box')
        if len(_):
            _ = self.extract_xpath(hxs, 'product_rating_value')
            if len(_):
                item['avg_reviews_points'] = _[0]
            _ = self.extract_xpath(hxs, 'product_num_reviews')
            if len(_):
                item['num_reviews'] = _[0]

        ## Optional Field
        # {{{
        item['product_spec'] = None
        item['cost_price'] = None
        item['keywords'] = None
        # }}}

        _ = self.extract_xpath(hxs, 'parse_product_super')
        if len(_):
            # product options
            base_product_name = item['product_name']
            regex = r"""new Product.Config\((.*)\);"""
            match_obj = re.search(regex, response.body)
            if match_obj is not None:
                json_str = match_obj.groups()[0]
                data = json.loads(json_str)
                regex = '''\"attributes\":{\"([\d]+)\"'''
                match_obj = re.search(regex, json_str)
                data_id = match_obj.groups()[0]
                options = data['attributes'][data_id]['options']
                for option in options:
                    new_item = copy.deepcopy(item)
                    new_item['product_name'] =\
                        '%s - %s' % (base_product_name, option['label'])
                    new_item['product_number'] = option['products'][0]
                    try:
                        price_increment = float(option['price'])
                        if price_increment:
                            new_item['sale_price'] += price_increment
                    except:
                        pass
                    if 'subProductsAvailability' in data:
                        for i in data['subProductsAvailability']:
                            if i['id'] == new_item['product_number']:
                                availability = i['availability'].lower()
                                if 'days' in availability:
                                    new_item['availability'] = ProductItem.AVAIL_IS
                                else:
                                    tmp = self.AVAIL_CHOICES.get(re.sub('\s+', '', availability))
                                    if not tmp:
                                        raise ValueError(u'No such Availability %s' % re.sub('\s+', '', _[0].strip().lower()))
                                    new_item['availability'] = tmp

                    yield self.make_shipping_cost_request(new_item,
                                                          response.url)
        else:
            if item['availability'] == ProductItem.AVAIL_OOS:
                yield item
            else:
                yield self.make_shipping_cost_request(item, response.url)
        # }}}

    def parse_shipping_cost(self, response):
        ''' '''  # {{{
        item = response.meta['item']
        item['shipping_cost'] = 0

        # self.log('Reading shipping cost for %s ' %
        #          response.meta['shipping_for'],
        #          level=log.DEBUG)

        # self.log('Response headers: %s ' %
        #          response.headers,
        #          level=log.DEBUG)
        # self.log('Response body: %s ' %
        #          response.body,
        #          level=log.DEBUG)

        if 'X-Json' in response.headers:
            # self.log('Got response: %s' % response.headers['X-Json'],
            #          level=log.DEBUG)
            carriers_data = json.loads(response.headers['X-Json'])
            if 'carriers' in carriers_data:
                price_more_than_zero = [i['price']
                                        for i in carriers_data['carriers']
                                        if 'price' in i and i['price'] > 0]
                if len(price_more_than_zero):
                    item['shipping_cost'] = price_more_than_zero[0]
                # if 'price' in carriers[0]:
                #     item['shipping_cost'] = float(carriers[0]['price'])

        # self.log('The result item is: %s' % str(item),
        #          level=log.DEBUG)

        return item

        # }}}
