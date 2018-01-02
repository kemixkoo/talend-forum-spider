#!/usr/bin/env python
# -*-coding:utf-8-*-
__author__ = 'Kemix Koo'

import logging
import os
import shutil
import time
from datetime import datetime

from conf.config import Config
from spider.categories import Category
from spider.topics import TopicList, Topic
from tool import utils


class Getoutofloop(Exception):
    pass


logger = logging.getLogger('spider')

startTime = datetime.now()

# categories
config = Config()
category = Category(config)

result_folder = config['spider.result_folder']
# clean the files folder
if os.path.exists(result_folder):
    shutil.rmtree(result_folder, True)

logger.info("################START( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################")
logger.info("-------------------------------------------")
# contents of topics
categories_list = category.details

utils.save_to_file(result_folder + '/summaries', category.stats)
utils.save_to_file(result_folder + '/categories', categories_list)

topiclist = TopicList(config)
topic = Topic(config)

redirect_url = []
total = 0

try:
    for category in categories_list:
        # category_path = category['path']
        category_id = category['id']
        category_pages = category['pages']

        logger.info((category_id, category_pages))

        if category_pages < 1:
            continue

        for cp in range(1, category_pages + 1):
            category_uri = utils.get_viewforum_uri(category_id, cp)
            category_list = topiclist.get_list(category_uri)

            # save to file
            category_out_file = str(category_id) + '-' + 'topicslist-' + str(cp)
            utils.save_to_file(result_folder + '/' + category_out_file, category_list)
            logger.info((len(category_list), category_out_file))

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
                topic_filename_prefix = str(category_id) + '-' + str(topic_id) + '-'
                post_out_file = topic_filename_prefix + 'topic-0'
                utils.save_to_file(result_folder + '/' + post_out_file, topic_post)
                logger.info((topic_pages, post_out_file))

                for tp in range(1, topic_pages + 1):
                    time.sleep(0.5)

                    total = total + 1
                    # if total > 100:
                    #     raise Getoutofloop()  # stop to test

                    each_page_url = utils.get_viewtopic_uri(topic_id, tp)
                    each_page_replies = topic.get_replies(each_page_url)
                    if each_page_replies:
                        each_replies_out_file = topic_filename_prefix + 'topic-' + str(tp)
                        utils.save_to_file(result_folder + '/' + each_replies_out_file, each_page_replies)
                        logger.info((len(each_page_replies), each_replies_out_file))



except Getoutofloop:
    pass
except Exception, e:
    logger.exception(str(e), exc_info=True)

if len(redirect_url) > 0:
    redirect_file = 'redirect_urls.json'
    utils.save_to_file(result_folder + '/' + redirect_file, redirect_url)
    logger.info((len(redirect_url), len(redirect_url)))

logger.info("################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################")
timeElapsed = datetime.now() - startTime
logger.info((total, 'Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed)))
