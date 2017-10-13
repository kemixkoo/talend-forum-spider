# -*-coding:utf-8-*-
__author__ = 'ggu'

from forum.tool.fmongo import MongoConn
from forum.tool.frequest import BS4Request


class Config:
    def __init__(self):
        self.config = {}

        # settings of forum site
        self.config['encoding'] = 'utf-8'
        self.config['url'] = 'https://www.talendforge.org/forum/'
        self.config['request.headers'] = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'}

        #settings of mongo db
        self.config['mongo.server'] = 'localhost'
        self.config['mongo.port'] = 27017

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

    def createmongo(self):
        return MongoConn(self)

    def createbs4(self, path=''):
        return BS4Request(self, path)
