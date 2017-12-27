# -*-coding:utf-8-*-
__author__ = 'ggu'

import ConfigParser
from os.path import split,realpath


class Config:
    def __init__(self):
        # load from config file
        self.__file_config = ConfigParser.ConfigParser()
        path = split(realpath(__file__))[0] + '/forum.conf'
        self.__file_config.read(path)

        # custom setting
        self.settings = {}

        self.settings['encoding'] = 'utf-8'

        # for site
        # self.settings['url'] = self.__file_config.get('site', 'url')
        self.settings['site.request_headers'] = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'}

        # init obj
        self.__bs4request = None
        self.__mongo = None

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
        if key and val and key in self.settings.keys():
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


