from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.contrib.spiders import CrawlSpider
from scraper.items import ProductItem

import re, lxml, json
from copy import deepcopy
from time import sleep

import ujson as json
from scrapy import log

class HarveynormanSpider(CrawlSpider):

    name = "harveynorman"
    store_url = "http://www.harveynorman.com.au/"
    start_urls = [
        store_url
    ]

    xpaths = {
        # {{{
        #'parse_categories': '//ul[@id="nav"]/li/a',
        'parse_categories': '//div[@id="nav"]//div[@class="_product"]/ul/li/a',
		'parse_sub_categories': '//ul[@class="sub-cat-list"]/li/ul/li/a',
        'parse_category_products': '//a[@class="name fn"]/@href',
        'parse_category_next': '//a[@id="btn-show-more"]/@onclick',

        'parse_product_name': '//span[@class="product-name"]/text()',
        'parse_product_description': '//div[@class="short-description"]',
		'parse_product_description_1': '//div[@class="description"]',
        'parse_product_manufacture':'//ul[@id="product-attribute-specs-table"]//h4[contains(text(),"General")]/following-sibling::ul[1]/li/div[contains(text(), "Brand")]/following-sibling::div[1]/text()',
        'parse_product_image_url': '//div[@id="img-holder"]/img/@src',
        'parse_product_number':'//input[@name="product_id"]/@value',
        'parse_product_availability': '//span[@class="offer-title"]/text()',
        'parse_product_availability_1': '//div[@class="in-store-only"]/text()',
        'parse_product_availability_2': '//span[@class="availability-msg"]/span/text()',
        'parse_product_sale_price': '//div[@class="cfx clear posrel"]/div[@class="price-device"]/span[@class="regular-price"]/span[@class="price"]/text()',
        'parse_product_sale_price_1': '//div[@class="cfx clear posrel"]/div[@class="price-device"]/div[@class="price-as-configured regular-price"]/span[@class="configured-price"]/span[@class="price"]/text()',
        'parse_product_sale_price_2': '//div[@class="cfx clear posrel"]/div[@class="price-device"]/div[@class="special-price"]/span[@class="special"]/span[@class="price"]/text()',
        'parse_product_sale_price_3': '//div[@class="cfx clear posrel"]/div[@class="price-device"]/span[@class="cashback regular-price"]/span[@class="before cfx"]/span[@class="price"]/text()',
        'parse_product_old_price': '',
        'parse_product_addcart_btn': '//button[@id="btn-add-to-cart"]',
        'parse_product_various':'//fieldset[@class="product-options"]/script[1]/text()',
        'parse_product_postcode':'//input[@name="estimate_postcode"]',
        'parse_product_mpn':'//ul[@id="product-attribute-specs-table"]//h4[contains(text(),"General")]/following-sibling::ul[1]/li/div[contains(text(), "Model")]/following-sibling::div[1]/text()',
        'parse_product_barcode':'//ul[@id="product-attribute-specs-table"]//h4[contains(text(),"General")]/following-sibling::ul[1]/li/div[contains(text(), "Barcode")]/following-sibling::div[1]/text()',
    } # }}}

    err_count = []
    SC_URL = u'http://www.harveynorman.com.au/shippingmethod/ajax/estimate/postcode/2000/ffgroup/%s/psize/%s'
    nextpage_url = u'http://www.harveynorman.com.au/endecasearch/result/ajaxShowMore?%s'

    def extract_xpath(self, hxs, name_xpath):
        # {{{
        xpath = self.xpaths[name_xpath]
        return hxs.select(xpath).extract()
        # }}}

    def error_page(self, failure):
        self.log(failure, level=log.INFO)

    def parse(self, response):
        # {{{
        # yield Request('http://www.harveynorman.com.au/sunbeam-mode-ironing-board-134601.html', callback=self.parse_product, meta={'category':''}, dont_filter=True, priority=1, errback=self.error_page)
        hxs = HtmlXPathSelector(response)
        categories = hxs.select(self.xpaths['parse_categories'])

        for category in categories[1:]:
            url = category.select('@href').extract()[0].strip()
            name = category.select('text()').extract()[0].strip()
            category_path=['Home']
            category_path.append(name)
            category_url = url
            if category_url[0] == '/':
                category_url = category_url[1:]
            if 'http' not in category_url:
                category_url = self.store_url + category_url
            yield Request(category_url, callback=self.parse_category, meta={'category':category_path}, errback=self.error_page)
        # }}}

    def parse_category(self, response):
        # {{{
        hxs = HtmlXPathSelector(response)
        sub_categories = hxs.select(self.xpaths['parse_sub_categories'])
        if len(sub_categories):
            for sub_category in sub_categories:
                url = sub_category.select('@href').extract()[0].strip()
                if "guides" in url:
                    continue
                name = sub_category.select('strong/text()').extract()[0].strip()
                category_path = deepcopy(response.meta['category'])
                category_path.append(name)
                sub_category_url = url
                if sub_category_url[0] == '/':
                    sub_category_url = sub_category_url[1:]
                if 'http' not in sub_category_url:
                    sub_category_url = self.store_url + sub_category_url
                yield Request(sub_category_url, callback=self.parse_sub_category, meta={'category':category_path}, errback=self.error_page)
        else:
            ret = self.parse_sub_category(response)
            for i in ret:
                yield i
        # }}}

    def parse_sub_category(self, response):
        # {{{
        hxs = HtmlXPathSelector(response)

        products = hxs.select(self.xpaths['parse_category_products']).extract()
        for url in products:
            product_url = url
            if product_url [0] == '/':
                product_url = product_url [1:]
            if 'http' not in product_url :
                product_url  = self.store_url + product_url
            yield Request(product_url,callback=self.parse_product, meta=response.meta, errback=self.error_page)

        show_more_str = hxs.select(self.xpaths['parse_category_next']).extract()
        if len(show_more_str):
            onclick_str = show_more_str[0]
            body = response.body.replace('\n', '').replace('\r', '')
            query_str = re.findall(r'jsonEndecaShowMore\((\'.*?\'),', body)
            query_str = query_str[0].replace('\'','')
            next_page_url = self.nextpage_url % query_str
            yield Request(next_page_url, callback=self.parse_sub_category, meta=response.meta, errback=self.error_page)
        # }}}

    def parse_product(self, response):
        # {{{
        if 'It may have been removed or no longer exists' in response.body:
            #print response.url
            #flag = False
            #if len(self.err_count):
            #    for i in self.err_count:
            #        if response.url in i:
            #            flag = True
            #            i[1] -= 1
            #            if i[1]:
            #                yield response.request
            #            break

            #if not flag:
            #    self.err_count.append([response.url, 2])
            #    yield response.request
            return

        hxs = HtmlXPathSelector(response)
        item = ProductItem()

        # Source
        item['source'] = self.store_url

        # Product Name
        tmp = self.extract_xpath(hxs, 'parse_product_name')
        if not len(tmp):
            raise ValueError('No Product Name')
        else:
            item['product_name'] = tmp[0].strip()

        # Manufacturer
        tmp = self.extract_xpath(hxs, 'parse_product_manufacture')
        if not len(tmp):
            item['manufacturer'] = ''
        else:
            item['manufacturer'] = tmp[0]

        # MPN
        tmp = self.extract_xpath(hxs, 'parse_product_mpn')
        if not len(tmp):
            item['mpn'] = ''
        else:
            item['mpn'] = tmp[0]

        # Barcode
        tmp = self.extract_xpath(hxs, 'parse_product_barcode')
        if not len(tmp):
            item['gtin'] = ''
        else:
            item['gtin'] = tmp[0]

        # Product Number
        tmp = self.extract_xpath(hxs, 'parse_product_number')
        if not len(tmp):
            raise ValueError('No Product Number')
        else:
            item['product_number'] = tmp[0]

        # Description
        tmp = hxs.select(self.xpaths['parse_product_description'])
        if not len(tmp):
            raise ValueError('No Description')
        else:
            description = []
            for i in tmp:
                text = lxml.html.fromstring(i.extract()).text_content()
                if text.strip() != '':
                    description.append(text)

            item['description'] = '\n'.join(map(lambda s: s.strip(), description)).strip()

        tmp = hxs.select(self.xpaths['parse_product_description_1'])
        if len(tmp):
            description = []
            for i in tmp:
                text = lxml.html.fromstring(i.extract()).text_content()
                if text.strip() != '':
                    description.append(text)

            item['description'] += '\n'.join(map(lambda s: s.strip(), description)).strip()

        # Categroy Name
        categories = response.meta['category']

        cg_paths = []
        cg_path = []

        for c in categories:
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

        # Product URL
        item['product_url'] = response.url

        # Image URL
        tmp = self.extract_xpath(hxs, 'parse_product_image_url')
        if not len(tmp):
            raise ValueError('No Image Url')
        else:
            item['image_url'] = tmp[0]

        # Product Condition
        item['product_condition'] = ProductItem.PC_NEW

        # On Sale
        item['on_sale'] = 0
        # if len(self.extract_xpath(hxs, 'parse_product_old_price')) > 0:
        #     item['on_sale'] = 1

        # Sale Price
        tmp = self.extract_xpath(hxs, 'parse_product_sale_price')
        if not len(tmp):
            tmp = self.extract_xpath(hxs, 'parse_product_sale_price_1')
        if not len(tmp):
            tmp = self.extract_xpath(hxs, 'parse_product_sale_price_2')
        if not len(tmp):
            tmp = self.extract_xpath(hxs, 'parse_product_sale_price_3')
        if not len(tmp):
            item['sale_price'] = -1
        else:
            tmp = tmp[0].strip()
            tmp = tmp.replace(',','')
            item['sale_price'] = float(tmp)

        # Availability
        tmp = self.extract_xpath(hxs, 'parse_product_availability')
        if not len(tmp):
            tmp = self.extract_xpath(hxs, 'parse_product_availability_1')
        if not len(tmp):
            item['availability'] = ProductItem.AVAIL_IS
        else:
            availability_str = tmp[0].lower()
            if "pre-order" in availability_str:
                item['availability'] = ProductItem.AVAIL_PO
            elif "in-store only" in availability_str:
                item['availability'] = ProductItem.AVAIL_ISO
            else:
                item['availability'] = ProductItem.AVAIL_OOS
                tmp = self.extract_xpath(hxs, 'parse_product_availability_2')
                if len(tmp):
                    availability_str = tmp[0].lower()
                    if "in-store only" in availability_str:
                        item['availability'] = ProductItem.AVAIL_ISO

        # Currency
        item['currency'] = 'AUD'

        #Various
        product_list = {}
        code_str = ''
        tmp = self.extract_xpath(hxs, 'parse_product_various')
        if len(tmp):
            try:
                code_str = tmp[0].replace('\n','').replace('\r','').strip()
                tmp = re.findall(r'new Product\.Config\((\{"attributes":.*?\}),"template":', code_str)
                tmp = tmp[0] + '}'
                json_data = json.loads(tmp)
                vals = json_data['attributes'].values()
                if len(vals):
                    for val in vals:
                        for option in val['options']:
                            for product in option['products']:
                                if not product_list.has_key(product):
                                    product_list[product] = []
                                product_list[product].append(option['label'])
            except:
                pass

        #AddCart Btn
        tmp = hxs.select(self.xpaths['parse_product_addcart_btn'])
        if not len(tmp):
            item['shipping_cost'] = -1
            if len(product_list):
                for i in product_list:
                    pattern = r'\"%s\":\{\"price\":\"(.*?)\",' % i
                    price = re.findall(pattern, code_str)[0].strip()
                    name = " - ".join(product_list[i])
                    id = "_".join(product_list[i])

                    vary_item = deepcopy(item)
                    vary_item['product_name'] += " - " + name
                    vary_item['product_number'] += "_" + id
                    vary_item['sale_price'] = float(price)
                    yield vary_item
            else:
                yield item
        else:
            #Shipping cost
            tmp = hxs.select(self.xpaths['parse_product_postcode'])
            if len(tmp):
                postcode = tmp[0]
                ffgroup = postcode.select('@data-ffgroup').extract()[0].strip()
                psize = postcode.select('@data-psize').extract()[0].strip()
                request = Request(
                    url=self.SC_URL % (ffgroup,psize),
                    meta={
                        'item':item,
                        'product_list':product_list,
                        'code_str':code_str,
                    },
                    callback=self.parse_shipping_cost,
                    errback=self.error_page,
                    dont_filter=True,
                )
                yield request
            else:
                item['shipping_cost'] = -1
                if len(product_list):
                    for i in product_list:
                        pattern = r'\"%s\":\{\"price\":\"(.*?)\",' % i
                        price = re.findall(pattern, code_str)[0].strip()
                        name = " - ".join(product_list[i])
                        id = "_".join(product_list[i])

                        vary_item = deepcopy(item)
                        vary_item['product_name'] += " - " + name
                        vary_item['product_number'] += "_" + id
                        vary_item['sale_price'] = float(price)
                        yield vary_item
                else:
                    yield item
        # }}}
    
    def parse_shipping_cost(self, response):
        # {{{
        data = json.loads(response.body)
        item = response.meta['item']
        product_list = response.meta['product_list']
        code_str = response.meta['code_str']

        shipping_cost = float(str(data['shipping_cost']).replace(',',''))
        item['shipping_cost'] = shipping_cost

        if len(product_list):
            for i in product_list:
                pattern = r'\"%s\":\{\"price\":\"(.*?)\",' % i
                price = re.findall(pattern, code_str)[0].strip()
                name = " - ".join(product_list[i])
                id = "_".join(product_list[i])

                vary_item = deepcopy(item)
                vary_item['product_name'] += " - " + name
                vary_item['product_number'] += "_" + id
                vary_item['sale_price'] = float(price)
                yield vary_item
        else:
            yield item
        # }}}
