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

prefix_file_name = '0-'

utils.save_to_file(result_folder + '/' + prefix_file_name + 'summaries', category.stats)
utils.save_to_file(result_folder + '/' + prefix_file_name + 'categories', categories_list)

topiclist = TopicList(config)
topic = Topic(config)

redirect_urls = []
empty_urls = []
total = 0

try:
    for category in categories_list:
        # category_path = category['path']
        category_id = category['id']
        category_pages = category['pages']

        if category_pages < 1:
            continue

        logger.info((category_id, category_pages))

        for cp in range(1, category_pages + 1):
            category_uri = utils.get_viewforum_uri(category_id, cp)
            category_list = topiclist.get_list(category_uri)

            # save to file
            prefix_topic_name = str(category_id) + '-topic-' + str(cp)
            category_out_file = prefix_topic_name + '-list'

            logger.info((len(category_list), category_out_file))
            utils.save_to_file(result_folder + '/' + category_out_file, category_list)

            time.sleep(0.3)

            for one_topic in category_list:
                time.sleep(0.3)
                topic_id = one_topic['topic_id']
                topic_url = utils.get_viewtopic_uri(topic_id)

                topic_pages = topic.get_pages(topic_url)
                if topic_pages is None or topic_pages < 1:
                    redirect_urls.append(topic_url)
                    continue  # didn't find the pages

                topic_post = topic.get_post(topic_url)
                if topic_post is None or len(topic_post) < 1:
                    empty_urls.append(topic_url)
                    continue  # even no post, empty topic

                topic_post['pages'] = topic_pages
                topic_post['url'] = topic_url

                # save to file
                topic_filename_prefix = prefix_topic_name + '-' + str(topic_id) + '-'
                post_out_file = topic_filename_prefix + '0'

                logger.info((topic_pages, post_out_file))
                utils.save_to_file(result_folder + '/' + post_out_file, topic_post)

                for tp in range(1, topic_pages + 1):
                    time.sleep(0.3)

                    total = total + 1
                    # if total > 100:
                    #     raise Getoutofloop()  # stop to test

                    each_page_url = utils.get_viewtopic_uri(topic_id, tp)
                    each_page_replies = topic.get_replies(each_page_url)

                    if each_page_replies is None or len(each_page_replies) < 1:
                        continue  # no any replies

                    each_page_replies_num = len(each_page_replies)
                    each_replies_out_file = topic_filename_prefix + str(tp) + '-' + str(each_page_replies_num)

                    logger.info((each_page_replies_num, each_replies_out_file))
                    utils.save_to_file(result_folder + '/' + each_replies_out_file, each_page_replies)



except Getoutofloop:
    pass
except Exception, e:
    logger.exception(str(e), exc_info=True)

if len(redirect_urls) > 0:
    redirect_file = result_folder + '/' + prefix_file_name + 'redirect_urls.json'
    utils.save_to_file(redirect_file, redirect_urls)
    logger.info((len(redirect_urls), redirect_file))

if len(empty_urls) > 0:
    empty_file = result_folder + '/' + prefix_file_name + 'empty_urls.json'
    utils.save_to_file(empty_file, empty_urls)
    logger.info((len(empty_urls), empty_file))

logger.info("################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################")
timeElapsed = datetime.now() - startTime
logger.info((total, 'Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed)))
