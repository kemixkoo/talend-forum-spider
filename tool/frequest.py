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
        self.__http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    def get_contents(self, path=''):
        full_url = self.__config['site.url'] + path

        req = self.__http.request('GET', full_url, headers=self.__config['site.request_headers'])
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
