# -*-coding:utf-8-*-
__author__ = 'ggu'

import urllib3
import urllib3.contrib.pyopenssl
import certifi
from bs4 import BeautifulSoup

urllib3.contrib.pyopenssl.inject_into_urllib3()


class Config:
    def __init__(self):
        self.config = {}
        self.config['encoding'] = 'utf-8'
        self.config['url'] = 'https://www.talendforge.org/forum/'
        self.config['request.headers'] = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'}

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        if key and key in self.config.keys():
            return self.config[key]
        else:
            return None

    def set(self, key, val):
        if key and val and key in self.config.keys():
            self.config[key] = val


class BS4Request:
    def __init__(self, path=''):
        self.config = Config()
        self.url = self.config['url'] + path

        # print('Request URL: ' + self.url)

        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        req = http.request('GET', self.url, headers=self.config['request.headers'], timeout=4.0)

        html_data = req.data.decode(self.config['encoding'])

        self.contents = BeautifulSoup(html_data, 'html.parser')

        req.release_conn()
