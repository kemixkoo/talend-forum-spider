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


def mongo_log(data, status='info'):
    mongo_data = {}
    mongo_data['message'] = str(data)
    mongo_data['time'] = time.strftime("%Y-%m-%d %H:%M:%S")

    if status == 'info':
        logger.info(data)
    if status == 'error':
        logger.error(data)

    mongo_data['status'] = status

    mongo.db.logs.insert(mongo_data)


def out_data(file, mongo_set, data, message=None):
    if data is None or len(data) < 1:
        return

    if message:
        mongo_log(message)

    if file:
        logger.info((os.path.split(file)[1], len(data)))
        utils.save_to_file(file, data)

    if mongo_set:
        mongo_set.insert(data)


def retrieveCategories():
    mongo_log('Starting to retrieve Categories')
    category = Category(config)

    summaries = category.stats
    categories_list = category.details

    category_base_path = result_folder + '/0-'
    summaries_out_file = category_base_path + 'summaries'
    categories_out_file = category_base_path + 'categories'

    out_data(summaries_out_file, mongo.db.summaries, summaries,
             message='Finished to retrieve summaries')
    out_data(categories_out_file, mongo.db.categories, categories_list,
             message='Finished to retrieve all Categories list ' + str(len(categories_list)))


def retrieveTopicList(one_category):
    # category_path = one_category['path']
    category_id = one_category['id']
    category_pages = one_category['pages']

    if category_pages < 1:
        mongo_log("Can't find any pages for " + str(category_id), status='error')
        return

    mongo_log('Starting to retrieve Topics list for ' + str(category_id) + ' with ' + str(category_pages) + ' pages')

    for cp in range(1, category_pages + 1):
        time.sleep(0.3)
        category_uri = utils.get_viewforum_uri(category_id, cp)
        message_suffix = ' for ' + str(category_id) + ' of ' + str(cp) + ' page from ' + category_uri
        mongo_log('Starting to retrieve Topics list' + message_suffix)

        topic_list = topiclist.get_list(category_uri)

        # save to file
        topic_file_name_prefix = str(category_id) + '-topic-' + str(cp)
        topic_list_out_file = result_folder + '/' + topic_file_name_prefix + '-list'

        out_data(topic_list_out_file, mongo.db.topiclist, topic_list,
                 message='Finished to retrieve all Topic list ' + str(len(topic_list)) + message_suffix)


def retrieveTopicPost(one_topic):
    topic_id = one_topic['topic_id']
    category_id = one_topic['category_id']
    category_page = one_topic['category_page']

    topic_url = utils.get_viewtopic_uri(topic_id)

    message_suffix = ' for ' + str(category_id) + '(' + str(category_page) + '),' + str(
        topic_id) + ' from ' + topic_url
    mongo_log('Starting to retrieve topic post' + message_suffix)

    topic_contents = topic.get_contents(topic_url)

    topic_pages = utils.get_pages(topic_contents)
    if topic_pages is None or topic_pages < 1:
        mongo_log("Can't find any pages" + message_suffix, status='error')
        redirect_urls.append(topic_url)
        return  # didn't find the pages

    topic_post = topic.get_post(topic_contents)
    if topic_post is None or len(topic_post) < 1:
        mongo_log("Can't find any post" + message_suffix, status='error')
        empty_urls.append(topic_url)
        return  # even no post, empty topic

    topic_post['pages'] = topic_pages
    topic_post['url'] = topic_url

    # set from topic
    topic_post['topic_id'] = topic_id
    topic_post['category_id'] = category_id
    topic_post['category_page'] = category_page

    # save to file
    # topic_file_name_prefix = str(category_id) + '-topic-' + str(category_page_index)
    # topic_file_name_prefix = topic_file_name_prefix + '-' + str(topic_id) + '-'
    # post_out_file = topic_file_name_prefix + '0'
    # utils.save_to_file(result_folder + '/' + post_out_file, topic_post)

    mongo.db.posts.insert(topic_post)
    mongo_log('Finished to retrieve topic post' + message_suffix + ' with ' + str(topic_pages) + ' pages')


def retrieveTopicReplies(one_post, current_page):
    topic_id = one_post['topic_id']
    category_id = one_post['category_id']
    category_page = one_post['category_page']

    each_page_url = utils.get_viewtopic_uri(topic_id, current_page)

    message_suffix = ' for ' + str(category_id) + '(' + str(category_page) + '),' + str(
        topic_id) + ' from ' + str(current_page) + ' page ' + each_page_url
    mongo_log('Starting to retrieve topic replies' + message_suffix)

    each_page_replies = topic.get_replies(each_page_url)

    if each_page_replies is None or len(each_page_replies) < 1:
        mongo_log("Can't find any replies" + message_suffix, status='error')
        empty_urls.append(each_page_url)
        return  # no any replies

    each_page_replies_num = len(each_page_replies)

    # topic_file_name_prefix = str(category_id) + '-topic-' + str(category_page_index)
    # topic_file_name_prefix = topic_file_name_prefix + '-' + str(topic_id) + '-'
    # each_replies_out_file = topic_file_name_prefix + str(current_page) + '-' + str(each_page_replies_num)
    # utils.save_to_file(result_folder + '/' + each_replies_out_file, each_page_replies)

    mongo.db.replies.insert(each_page_replies)
    mongo_log('Finished to retrieve topic replies' + str(each_page_replies_num) + message_suffix)


if __name__ == "__main__":
    mongo_log("################START################")

    try:

        retrieveCategories()
        for s in mongo.db.summaries.find():
            print 'Summaries: ' + str(s)

        for one_category in mongo.db.categories.find():
            time.sleep(0.3)
            # print(one_category)
            retrieveTopicList(one_category)
        print 'Categories: ' + str(mongo.db.categories.count())

        # spent about 1.5 hours

        # for one_topic in mongo.db.topiclist.find():
        #     time.sleep(0.3)
        #     # print one_topic
        #     retrieveTopicPost(one_topic)
        # print 'TopicList: ' + str(mongo.db.topiclist.count())
        #
        # # spent about 12 hours
        #
        # for one_post in mongo.db.posts.find():
        #     pages = int(one_post['pages'])
        #
        #     for tp in range(1, pages + 1):
        #         time.sleep(0.3)
        #         retrieveTopicReplies(one_post, tp)

    except Exception, e:
        mongo_log(str(e), status='error')
        logger.exception(str(e), exc_info=True)

    out_data(result_folder + '/0-redirect_urls.json', mongo.db.redirect, {'urls': redirect_urls},
             message='Existed ' + str(len(redirect_urls)))
    out_data(result_folder + '/0-empty_urls.json', mongo.db.empty, {'urls': empty_urls},
             message='Existed ' + str(len(empty_urls)))

    #
    timeElapsed = datetime.now() - startTime
    mongo_log('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))
    mongo_log("################END################")
