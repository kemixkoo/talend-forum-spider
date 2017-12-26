# -*-coding:utf8-*-
__author__ = 'ggu'

from pymongo import MongoClient


class MongoConn:
    def __init__(self, config):
        server = config['mongo.server']
        port = config['mongo.port']

        self.__connection = MongoClient(server, port)
        self.__db = self.__connection.forum

    def add_categories(self, data):
        categories = self.__db.categories
        categories.insert(data)

    def add_topiclist(self, data):
        topiclist = self.__db.topiclist
        topiclist.insert(data)

    def add_topic(self, data):
        topics = self.__db.topics
        topics.insert(data)
