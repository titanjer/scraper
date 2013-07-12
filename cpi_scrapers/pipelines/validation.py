# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem

from cpi_scrapers.items import ProductItem


class ProductValidationPipeline(object):

    def process_item(self, item, spider):
        ''' ''' # {{{

        ## Required Fields
        for field in ProductItem.VALIDATION_REQUIRED:
            if field not in item:
                raise DropItem('Missing %s in Item' % field)

        ## Non-Required Field
        for field in ProductItem.VALIDATION_NON_REQUIRED:
            if field not in item:
                item[field] = None

        ## check Field Length
        # {{{
        for field, length in ProductItem.VALIDATION_LEN.items():
            tmp = item.get(field)
            if tmp is None:
                item[field] = ""
                continue

            if isinstance(tmp, basestring):
                #print 'Check Field Length: (%s, %s, %s, "%s")' % (field, length, len(tmp), tmp)
                tmp = tmp.strip()
                if len(tmp) > length:
                    raise DropItem('Wrong string format: %s | "%s"' % (field, tmp))
                item[field] = tmp
            else:
                raise DropItem('Not string: %s | "%s"' % (field, tmp))
        # }}}            
        
        ## Product Name
        if item['product_name'] == '':
            raise DropItem("Wrong Product Name! It's blank!")

        ## Category Name
        # {{{
        tmp_cgps = []
        for cgp in item['category_name'].split(ProductItem.CG_PATHS_SEP):
            tmp_cgp = []
            for cg in cgp.split(ProductItem.CG_PATH_SEP):
                cg = cg.strip()
                if cg != '':
                    tmp_cgp.append(cg)
            tmp = ProductItem.CG_PATH_SEP.join(tmp_cgp)
            if tmp != '':
                tmp_cgps.append(tmp)

        tmp = ProductItem.CG_PATHS_SEP.join(tmp_cgps)
        if tmp != item['category_name']:
            raise DropItem('Wrong format for category_name, %s' % item['category_name'])
        # }}}

        ## Product condition
        tmp = item['product_condition'] 
        if not (0 < tmp <= ProductItem.NUM_PC_OPTS):
            raise DropItem('Wrong Product Condition')
        
        ## Availability
        tmp = item['availability'] 
        if not (0 < tmp <= ProductItem.NUM_AVAIL_OPTS):
            raise DropItem('Wrong Availability')

        ## On Sale
        if item['on_sale'] not in (0, 1):
            raise DropItem('Wrong On Sale')

        ## Sale_price and its flag
        # {{{
        tmp = item['sale_price']
        if not isinstance(tmp, (int, float, long)):
            raise DropItem('Wrong type for sale_price')

        if tmp < 0:
            item['sale_price'] = 0
            item['no_sale_price'] = 1
        else:
            item['no_sale_price'] = 0
        # }}}

        ## Shipping cost and its flag
        # {{{
        tmp = item['shipping_cost']
        if not isinstance(tmp, (int, float, long)):
            raise DropItem('Wrong type for shipping_cost')

        if tmp < 0:
            item['shipping_cost'] = 0
            item['no_shipping_cost'] = 1
        else:
            item['no_shipping_cost'] = 0
        # }}}

        return item
        
        # }}}
        
