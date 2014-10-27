# Scrapy settings for scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'scraper'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Crawl responsibly by identifying yourself on the user-agent
USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 '
              'Safari/537.36')

LOG_LEVEL = 'INFO'
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = [
    'scraper.pipelines.validation.ProductValidationPipeline',
    'scraper.pipelines.items_rq.AddItemPipeline',
]

COOKIES_ENABLED = True


# Redis Pipeline
REDIS_HOST = '10.8.0.1'
REDIS_PORT = 6379
REDIS_DB = 0


# Local Settings
try:
    from local_settings import *
except ImportError:
    pass
