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
from tool.fmongo import MongoConn

logger = logging.getLogger('spider')

startTime = datetime.now()
logger.info("################START( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################")
logger.info("-------------------------------------------")

config = Config()
mongo = MongoConn(config)
topiclist = TopicList(config)
topic = Topic(config)

result_folder = config['spider.result_folder']
# clean the files folder
if os.path.exists(result_folder):
    shutil.rmtree(result_folder, True)

redirect_urls = []
empty_urls = []
total = 0


def retrieveCategories():
    category = Category(config)

    summaries = category.stats
    categories_list = category.details

    category_base_path = result_folder + '/0-'
    summaries_out_file = category_base_path + 'summaries'
    categories_out_file = category_base_path + 'categories'

    utils.save_to_file(summaries_out_file, summaries)
    utils.save_to_file(categories_out_file, categories_list)

    logger.info((os.path.split(categories_out_file)[1], len(categories_list)))

    mongo.db.summaries.insert(summaries)
    mongo.db.categories.insert(categories_list)


def retrieveTopicList(one_category):
    # category_path = one_category['path']
    category_id = one_category['id']
    category_pages = one_category['pages']

    if category_pages < 1:
        return

    logger.info((category_id, category_pages))

    for cp in range(1, category_pages + 1):
        time.sleep(0.3)
        category_uri = utils.get_viewforum_uri(category_id, cp)
        topic_list = topiclist.get_list(category_uri)

        # save to file
        topic_file_name_prefix = str(category_id) + '-topic-' + str(cp)
        topic_list_out_file = topic_file_name_prefix + '-list'

        logger.info((len(topic_list), topic_list_out_file))
        utils.save_to_file(result_folder + '/' + topic_list_out_file, topic_list)
        mongo.db.topiclist.insert(topic_list)


def retrieveTopicPost(one_topic):
    topic_id = one_topic['topic_id']
    category_id = one_topic['category_id']
    category_page_index = one_topic['category_page_index']

    topic_url = utils.get_viewtopic_uri(topic_id)

    topic_contents = topic.get_contents(topic_url)

    topic_pages = utils.get_pages(topic_contents)
    if topic_pages is None or topic_pages < 1:
        redirect_urls.append(topic_url)
        return  # didn't find the pages

    topic_post = topic.get_post(topic_contents)
    if topic_post is None or len(topic_post) < 1:
        empty_urls.append(topic_url)
        return  # even no post, empty topic

    topic_post['pages'] = topic_pages
    topic_post['url'] = topic_url

    # set from topic
    topic_post['topic_id'] = topic_id
    topic_post['category_id'] = category_id
    topic_post['category_page_index'] = category_page_index

    # save to file
    topic_file_name_prefix = str(category_id) + '-topic-' + str(category_page_index)
    topic_file_name_prefix = topic_file_name_prefix + '-' + str(topic_id) + '-'
    post_out_file = topic_file_name_prefix + '0'

    logger.info((topic_pages, post_out_file))
    # utils.save_to_file(result_folder + '/' + post_out_file, topic_post)
    mongo.db.posts.insert(topic_post)


def retrieveTopicReplies(one_post, current_page):
    topic_id = one_post['topic_id']
    category_id = one_post['category_id']
    category_page_index = one_post['category_page_index']

    each_page_url = utils.get_viewtopic_uri(topic_id, current_page)
    each_page_replies = topic.get_replies(each_page_url)

    if each_page_replies is None or len(each_page_replies) < 1:
        return  # no any replies

    each_page_replies_num = len(each_page_replies)

    topic_file_name_prefix = str(category_id) + '-topic-' + str(category_page_index)
    topic_file_name_prefix = topic_file_name_prefix + '-' + str(topic_id) + '-'
    each_replies_out_file = topic_file_name_prefix + str(current_page) + '-' + str(each_page_replies_num)

    logger.info((each_page_replies_num, each_replies_out_file))
    # utils.save_to_file(result_folder + '/' + each_replies_out_file, each_page_replies)
    mongo.db.replies.insert(each_page_replies)


try:
    retrieveCategories()

    for one_category in mongo.db.categories.find():
        time.sleep(0.3)
        retrieveTopicList(one_category)

    # for one_topic in mongo.db.topiclist.find():
    #     time.sleep(0.3)
    #     retrieveTopicPost(one_topic)
    #
    # for one_post in mongo.db.posts.find():
    #     pages = int(one_post['pages'])
    #
    #     for tp in range(1, pages + 1):
    #         time.sleep(0.3)
    #         retrieveTopicReplies(one_post, tp)



except Exception, e:
    logger.exception(str(e), exc_info=True)

if len(redirect_urls) > 0:
    redirect_file = result_folder + '/' + '0-redirect_urls.json'
    utils.save_to_file(redirect_file, redirect_urls)
    logger.info((len(redirect_urls), redirect_file))

if len(empty_urls) > 0:
    empty_file = result_folder + '/' + '0-empty_urls.json'
    utils.save_to_file(empty_file, empty_urls)
    logger.info((len(empty_urls), empty_file))

logger.info("################END( " + time.strftime("%Y-%m-%d %H:%M:%S") + " )################")
timeElapsed = datetime.now() - startTime
logger.info((total, 'Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed)))
