# -*-coding:utf-8-*-
__author__ = 'ggu'

import certifi
import urllib3
import urllib3.contrib.pyopenssl
from bs4 import BeautifulSoup

urllib3.contrib.pyopenssl.inject_into_urllib3()


class BS4Request:
    def __init__(self, config):
        self.__config = config
        self.__http = urllib3.PoolManager(headers=self.__config['site.request_headers'],
                                          timeout=urllib3.Timeout(connect=3, read=5.0), cert_reqs='CERT_REQUIRED',
                                          retries=urllib3.Retry(5, redirect=2),
                                          ca_certs=certifi.where())

    def get_contents(self, path=''):
        full_url = self.__config['site.url'] + path
        count = 0
        req = None
        while (req is None and count < 10):
            try:
                req = self.__http.request('GET', full_url)
                count += 1
            except Exception:
                import time
                time.sleep(0.5)

        # import requests
        # req = requests.session()
        # one_proxy = self.__config.get_random_proxy()
        # if one_proxy:
        #     req.proxies = self.__config.get_random_proxy()
        # resp = req.get(full_url, headers=self.__config['site.request_headers'],verify=False)

        html_data = req.data.decode(self.__config['encoding'])

        contents = BeautifulSoup(html_data, 'html.parser')

        req.release_conn()
        return contents
