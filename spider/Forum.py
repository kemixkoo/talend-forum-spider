#!/usr/bin/env python
# -*-coding:utf-8-*-
__author__ = 'ggu'

import os
import shutil
import time
from datetime import datetime

from config import Config
from spider.categories import Category
from spider.topics import TopicList, Topic
from tool import utils


class Getoutofloop(Exception):
    pass


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
topic = Topic(config)

redirect_url = []
total = 0;
try:
    for category in categories_list:
        # category_path = category['path']
        category_id = category['id']
        category_pages = category['pages']

        print (category_id, category_pages)

        if category_pages < 1:
            continue

        for cp in range(1, category_pages + 1):
            category_uri = utils.get_viewforum_uri(category_id, cp)
            category_list = topiclist.get_list(category_uri)

            # save to file
            category_out_file = "topicslist-" + str(category_id) + "-" + str(cp)
            print(category_out_file)
            utils.save_to_file(category_out_file + ".json", category_list)

            time.sleep(0.5)

            for one_topic in category_list:
                time.sleep(0.3)
                topic_id = one_topic['topic_id']
                topic_url = utils.get_viewtopic_uri(topic_id)

                topic_pages = topic.get_pages(topic_url)
                if topic_pages < 1:
                    redirect_url.append(topic_url)
                    continue

                topic_post = topic.get_post(topic_url)
                topic_post['pages'] = topic_pages

                # save to file
                post_out_file = "topic-" + str(topic_id) + "-0"
                print(topic_pages, post_out_file)
                utils.save_to_file(post_out_file + ".json", topic_post)

                for tp in range(1, topic_pages + 1):
                    time.sleep(0.5)

                    total = total + 1
                    # if total > 100:
                    #     raise Getoutofloop()  # stop to test

                    each_page_url = utils.get_viewtopic_uri(topic_id, tp)
                    each_page_replies = topic.get_replies(each_page_url)
                    if each_page_replies:
                        each_replies_out_file = "topic-" + str(topic_id) + "-" + str(tp)
                        print(len(each_page_replies), each_replies_out_file)
                        utils.save_to_file(each_replies_out_file + ".json", each_page_replies)
                        print "################Finished at( " + time.strftime(
                            "%Y-%m-%d %H:%M:%S") + " )################"


except Getoutofloop:
    pass

if len(redirect_url) > 0:
    utils.save_to_file('redirect_urls.json', redirect_url)

print "################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################"
timeElapsed = datetime.now() - startTime
print(total, 'Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))
