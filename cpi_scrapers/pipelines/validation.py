# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem

from cpi_scrapers.items import ProductItem


class ProductValidationPipeline(object):

    def process_item(self, item, spider):
        ''' ''' # {{{

        # Required Fields
        for field in ProductItem.VALIDATION_REQUIRED:
            if field not in item:
                raise DropItem('Missing %s in Item', field)

        # Non-Required Field
        for field in ProductItem.VALIDATION_NON_REQUIRED:
            if field not in item:
                item[field] = None

        # Length
        for field, length in ProductItem.VALIDATION_LEN.iteritems():
            tmp = item.get(field)
            if tmp and (not isinstance(tmp, basestring) or len(tmp) > length):
                raise DropItem('Wrong string format: %s | "%s"', field, tmp)
        
        # product condition
        tmp = item['product_condition'] 
        if not (0 < tmp <= ProductItem.NUM_PC_OPTS):
            raise DropItem('Wrong Product Condition')
        
        tmp = item['availability'] 
        if not (0 < tmp <= ProductItem.NUM_AVAIL_OPTS):
            raise DropItem('Wrong Availability')

        if item['on_sale'] not in (0, 1):
            raise DropItem('Wrong On Sale')
    
        return item
        
        # }}}
        
