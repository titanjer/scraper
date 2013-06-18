# Scrapy settings for cpi_scrapers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'cpi_scrapers'

SPIDER_MODULES = ['cpi_scrapers.spiders']
NEWSPIDER_MODULE = 'cpi_scrapers.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cpi_scrapers (+http://www.yourdomain.com)'


LOG_LEVEL = 'INFO'


try:
    from local_settings import *
except ImportError:
    pass
