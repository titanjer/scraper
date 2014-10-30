
# scraper specific item pipelines
# 1. product validation
# 2. push product to queue
ITEM_PIPELINES = [
    'scraper.pipelines.validation.ProductValidationPipeline',
    'scraper.pipelines.items_rq.AddItemPipeline',
]


# Redis Queue
RQ_QUEUE = 'scraper'


# Proxy
# PROXY_URL = 'http://localhost:8118'
# PROXY_AUTH = ''  # "USERNAME:PASSWORD"

DOWNLOADER_MIDDLEWARES = {
    # 'scraper.middlewares.ProxyMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 500,
    'proxies.Proxies': 740,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 750,
}


# Retry middlewares settings, 524 is for CloudFlare
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 520, 524]

# webdriver
DOWNLOAD_HANDLERS = {
    'http': 'scrapy_webdriver.download.WebdriverDownloadHandler',
    'https': 'scrapy_webdriver.download.WebdriverDownloadHandler',
}

SPIDER_MIDDLEWARES = {
    'scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
}

WEBDRIVER_BROWSER = 'PhantomJS'

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
