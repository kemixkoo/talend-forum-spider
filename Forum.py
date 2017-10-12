#!/usr/bin/env python
# -*-coding:utf-8-*-
__author__ = 'ggu'

import time
import json
import topics
from categories import Category


def format_data(data):
    return json.dumps(data, indent=2)


print "################START( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"

# categories
category = Category()
print format_data(category.stats)
print format_data(category.details)

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
                        topiclist = topics.TopicList(value).list
                        print format_data(topiclist)


print "################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"
