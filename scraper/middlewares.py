import base64


class ProxyMiddleware(object):

    def __init__(self, settings):
        self.proxy_url = settings.get('PROXY_URL')
        self.proxy_auth = settings.get('PROXY_AUTH')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if self.proxy_url:
            request.meta['proxy'] = self.proxy_url

            if self.proxy_auth:
                auth = base64.encodestring(self.proxy_auth)
                request.headers['Proxy-Authorization'] = 'Basic ' + auth
