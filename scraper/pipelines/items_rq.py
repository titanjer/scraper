
from twisted.internet.threads import deferToThread
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.exceptions import DropItem

from scraper.items import ProductItem

import rq
import redis


class AddItemPipeline(object):
    """ Pushes serialized item into a RQ """

    def __init__(self, host, port, db, queue_name, store_id):
        self.encoder = ScrapyJSONEncoder()
        self.store_id = store_id
        self.queue_name = queue_name

        self.server = redis.Redis(host, port, db)
        self.queue = rq.Queue(queue_name, connection=self.server)

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        db = settings.get('REDIS_DB', 0)
        queue_name = settings.get('RQ_QUEUE', 'default')
        store_id = int(settings.get('STORE', 0))
        return cls(host, port, db, queue_name, store_id)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        ''' ''' # {{{

        ## get global Store URL mapping
        store_id = self.store_id
        if store_id is 0:
            raise DropItem('Not set the store and no Store URL mapping')

        ## assign queue parameters
        item['store_id'] = store_id
        callback = 'worker.save_product_to_db'
        event = self.encoder.encode(dict(queue=self.queue_name, value=item))

        ## push item to redis queue
        self.queue.enqueue(callback, event)
        
        return item

        # }}}
