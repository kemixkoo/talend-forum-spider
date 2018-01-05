# -*-coding:utf8-*-
__author__ = 'ggu'

from pymongo import MongoClient


class MongoConn:
    def __init__(self, config):
        server = config['mongo.server']
        port = config['mongo.port']

        self.__connection = MongoClient(server, int(port))
        self.db = self.__connection.forum
