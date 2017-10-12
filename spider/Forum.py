#!/usr/bin/env python
# -*-coding:utf-8-*-
__author__ = 'ggu'

import json
import time
from forum.spider.categories import Category
from forum.spider.topics import TopicList


def format_data(data):
    return json.dumps(data, indent=2)


print "################START( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"

# categories
category = Category()
# print format_data(category.stats)
# print format_data(category.details)

print "-------------------------------------------"
# contents of topics
categories_list = category.details
for (top_title, sub_data) in categories_list.items():
    if isinstance(sub_data, dict):
        for (sub_title, data) in sub_data.items():
            if isinstance(data, dict):
                for (key, value) in data.items():
                    if key == 'path':
                        print "--------------------------------------"
                        print sub_title + "===> path:" + value
                        topiclist = TopicList(value)
                        # print format_data(topiclist.list)
                        print (topicList.pages, len(topicList.list))

print "################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"
