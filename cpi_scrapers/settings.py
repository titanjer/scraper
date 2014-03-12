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

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scraper (+http://www.yourdomain.com)'


LOG_LEVEL = 'INFO'
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = [
    'scraper.pipelines.validation.ProductValidationPipeline',
]
 
try:
    from local_settings import *
except ImportError:
    pass
