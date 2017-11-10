#!/usr/bin/env python
# -*-coding:utf-8-*-
__author__ = 'ggu'

import time
from forum.spider.categories import Category
from forum.config import Config
from forum.spider.topics import TopicList
from forum.tool.utils import save_to_file

print "################START( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"

# categories
config = Config()
category = Category(config)

print "-------------------------------------------"
# contents of topics
categories_list = category.details

save_to_file("categories-0.json", category.stats)
save_to_file("categories-1.json", categories_list)

topiclist = TopicList(config)

for item in categories_list:
    path = item['path']
    category_id = item['category_id']
    topiclist.get_list(path)

print "################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"
