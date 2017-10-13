# -*-coding:utf-8-*-
__author__ = 'ggu'

import urllib3
import urllib3.contrib.pyopenssl
import certifi
from bs4 import BeautifulSoup

urllib3.contrib.pyopenssl.inject_into_urllib3()


class BS4Request:
    def __init__(self, config, path=''):
        self.url = config['url'] + path

        # print('Request URL: ' + self.url)

        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        req = http.request('GET', self.url, headers=config['request.headers'], timeout=4.0)

        html_data = req.data.decode(config['encoding'])

        self.contents = BeautifulSoup(html_data, 'html.parser')

        req.release_conn()
