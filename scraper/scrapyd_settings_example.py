
# Redis Queue
RQ_QUEUE = 'scraper'

# Proxy
PROXY_URL = 'http://localhost:8118'
PROXY_AUTH = ''  # "USERNAME:PASSWORD"

DOWNLOADER_MIDDLEWARES = {
    'scraper.middlewares.ProxyMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
}


# webdriver
DOWNLOAD_HANDLERS = {
    'http': 'scrapy_webdriver.download.WebdriverDownloadHandler',
    'https': 'scrapy_webdriver.download.WebdriverDownloadHandler',
}

SPIDER_MIDDLEWARES = {
    'scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
}

WEBDRIVER_BROWSER = 'PhantomJS'

# Optional passing of parameters to the webdriver
WEBDRIVER_OPTIONS = {
    'service_args': [
        '--debug=false',
        '--load-images=false',
        '--webdriver-loglevel=info',
        '--ssl-protocol=any',
        '--proxy=localhost:8118',
        '--proxy-type=http',
    ]
}
