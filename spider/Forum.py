#!/usr/bin/env python
# -*-coding:utf-8-*-
__author__ = 'ggu'

import time, shutil, os
from forum.config import Config
from forum.spider.categories import Category
from forum.spider.topics import TopicList
from forum.tool import utils

print "################START( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"

# clean the files folder
target_files_folder = utils.get_target_files()
if os.path.exists(target_files_folder):
    shutil.rmtree(target_files_folder)

# categories
config = Config()
category = Category(config)

print "-------------------------------------------"
# contents of topics
categories_list = category.details

utils.save_to_file("summaries.json", category.stats)
utils.save_to_file("categories.json", categories_list)

topiclist = TopicList(config)

for item in categories_list:
    path = item['path']
    category_id = item['id']
    pages = item['pages']

    print (category_id, pages)

    if pages < 1:
        continue

    # for p in range(1, pages):
    #     uri = utils.get_viewforum_uri(category_id, p)
    #     result = topiclist.get_list(uri)
    #
    #     # save to file
    #     current_file = "topicslist-" + str(category_id) + "-" + str(p)
    #     utils.save_to_file(current_file, result)

        # for one_topic in result:

print "################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"
