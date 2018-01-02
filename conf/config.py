# -*-coding:utf-8-*-
__author__ = 'ggu'

import ConfigParser
import logging.config
import os
import shutil
from os.path import split, realpath


class Config:
    def __init__(self):
        self.__file_config = ConfigParser.ConfigParser()
        base_path = split(realpath(__file__))[0]

        # load from config file
        self.__file_config.read(base_path + '/forum.conf')

        # custom setting
        self.settings = {}

        default_target_folder = base_path + '/../target'
        if not os.path.exists(default_target_folder):
            os.makedirs(default_target_folder)

        # set spider result folder
        spider_result_folder = self.__getitem__('spider.result_folder')
        if spider_result_folder:
            # if relative path, add target
            if not spider_result_folder.startswith('/'):
                spider_result_folder = default_target_folder + '/' + spider_result_folder
        else:
            spider_result_folder = default_target_folder + '/files'

        if not os.path.exists(spider_result_folder):
            os.makedirs(spider_result_folder)

        self.set('spider.result_folder', spider_result_folder)

        # load logger
        default_log_folder = base_path + '/../log'
        shutil.rmtree(default_log_folder, True)
        if not os.path.exists(default_log_folder):
            os.makedirs(default_log_folder)

        logging.config.fileConfig(base_path + '/logging.conf')

        # encoding
        self.set('encoding', 'utf-8')

        # for site
        self.set('site.request_headers', {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'})

        # init obj
        self.__bs4request = None
        self.__mongo = None
        self.__proxies = None

    def __getitem__(self, key):
        value = self.get(key)
        if value:
            return value
        else:
            keys = key.split('.')
            if len(keys) > 1:
                return self.__file_config.get(keys[0], keys[1])

        return None

    def get(self, key):
        if key and key in self.settings.keys():
            return self.settings[key]
        else:
            return None

    def set(self, key, val):
        # if key and val and key in self.settings.keys():
        self.settings[key] = val

    def get_bs4request(self):
        if not self.__bs4request:
            from tool.frequest import BS4Request
            self.__bs4request = BS4Request(self)
        return self.__bs4request

    def get_mongo(self):
        if not self.__mongo:
            from tool.fmongo import MongoConn
            self.__mongo = MongoConn(self)
        return self.__mongo

    def get_proxies(self):
        if not self.__proxies:
            proxis_file = split(realpath(__file__))[0] + '/proxies.json'
            # self.__proxies = json.loads(open(proxis_file, 'r').read().replace("'", '"').replace("u", ''))
        return self.__proxies

    def get_random_proxy(self, type='https'):
        proxies = self.get_proxies()
        if len(proxies) > 0:
            import random
            proxy_ip = random.choice(proxies[type])
            proxies = {type: proxy_ip}
            # print proxies
            return proxies
