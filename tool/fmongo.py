# -*-coding:utf8-*-
__author__ = 'ggu'

import pymongo


class MongoConn:
    def __init__(self, config):
        server = config['mongo.server']
        port = config['mongo.port']

        self.__connection = pymongo.Connection(server, port)
        self.__db = self.__connection.forum

    def addcategories(self, data):
        categories = self.__db.categories
        categories.insert(data)

    def addtopiclist(self, data):
        topiclist = self.__db.topiclist
        topiclist.insert(data)

    def addtopic(self, data):
        topics = self.__db.topics
        topics.insert(data)
