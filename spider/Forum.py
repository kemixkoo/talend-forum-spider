#!/usr/bin/env python
# -*-coding:utf-8-*-
__author__ = 'ggu'

import os
import shutil
import time
from datetime import datetime

from config import Config
from spider.categories import Category
from spider.topics import TopicList
from tool import utils

startTime = datetime.now()
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

    for p in range(1, pages):
        time.sleep(0.3)
        uri = utils.get_viewforum_uri(category_id, p)
        result = topiclist.get_list(uri)

        # save to file
        current_file = "topicslist-" + str(category_id) + "-" + str(p)
        print(current_file)
        utils.save_to_file(current_file + ".json", result)


        for one_topic in result:
            time.sleep(0.3)
            topic_id=one_topic['topic_id']
            topic_url = utils.get_viewtopic_uri(topic_id)



print "################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"
timeElapsed = datetime.now() - startTime
print('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))
