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
no_replies_urls = []


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

    if file and data:
        logger.info((os.path.split(file)[1], len(data)))
        utils.save_to_file(file, data)

    if message:
        mongo_log(message)

    if mongo_set and data:
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
    category_id = one_category['category_id']
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

    topic_post['url'] = topic_url

    # set from topic
    topic_post['topic_id'] = topic_id
    topic_post['category_id'] = category_id
    topic_post['category_page'] = category_page

    # check the replies
    first_replies = topic.get_replies(topic_contents)
    if first_replies is None or len(first_replies) < 1:
        topic_post['replies'] = 0
    else:
        topic_post['replies'] = -1  # not sure

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

    message_suffix = ' for category' + str(category_id) + '(page:' + str(category_page) + '), topic ' + str(
        topic_id) + ' from ' + str(current_page) + ' page ' + each_page_url
    mongo_log('Starting to retrieve topic replies' + message_suffix)

    topic_contents = topic.get_contents(each_page_url)
    each_page_replies = topic.get_replies(topic_contents)

    if each_page_replies is None or len(each_page_replies) < 1:
        mongo_log("Can't find any replies" + message_suffix, status='error')
        no_replies_urls.append(each_page_url)
        return  # no any replies

    each_page_replies_num = len(each_page_replies)

    # topic_file_name_prefix = str(category_id) + '-topic-' + str(category_page_index)
    # topic_file_name_prefix = topic_file_name_prefix + '-' + str(topic_id) + '-'
    # each_replies_out_file = topic_file_name_prefix + str(current_page) + '-' + str(each_page_replies_num)
    # utils.save_to_file(result_folder + '/' + each_replies_out_file, each_page_replies)

    mongo.db.replies.insert(each_page_replies)
    mongo_log('Finished to retrieve topic replies ' + str(each_page_replies_num) + message_suffix)


def doRetrieveTopicList():
    # 1. Categories
    retrieveCategories()

    for s in mongo.db.summaries.find():
        print 'Summaries: ' + str(s)
    mongo_log('Categories: ' + str(mongo.db.categories.count()))  # 25

    # 2. Topics list
    for one_category in mongo.db.categories.find():
        mongo_log(one_category)
        retrieveTopicList(one_category)
    mongo_log('TopicList: ' + str(mongo.db.topiclist.count()))  # 42025


def doRetrieveTopics(post=True, reply=True):
    # 3. retrieve all topics
    for one_category in mongo.db.categories.find():
        category_id = one_category['category_id']
        category_pages = one_category['pages']

        for category_page in range(1, category_pages + 1):
            # no moved topic
            found_topiclist = mongo.db.topiclist.find(
                {'category_id': category_id, 'category_page': category_page, 'is_moved': 0})
            if found_topiclist is None or found_topiclist.count() < 1:
                mongo_log("Can't find any topic for category :" + str(category_id))
                continue

            for one_topic in found_topiclist:

                # 3.1 all posts
                if post:
                    retrieveTopicPost(one_topic)

                # 3.2 all replies, must be done 3.1 for posts
                if reply:
                    topic_id = one_topic['topic_id']
                    found_posts = mongo.db.posts.find(
                        {'topic_id': topic_id, 'has_replies': 1})
                    if found_posts is None or found_posts.count() < 1:
                        mongo_log("Can't find any replies for topic :" + str(topic_id))
                        continue

                    for one_post in found_posts:
                        topic_pages = one_post['pages']

                        for topic_page in range(1, topic_pages + 1):
                            retrieveTopicReplies(one_post, topic_page)

    # log
    if post:
        mongo_log('Posts: ' + str(mongo.db.posts.count()))
    if reply:
        mongo_log('Replies: ' + str(mongo.db.replies.count()))


def out_array_data(filename, arrData, mongoSet):
    if arrData:
        out_data(result_folder + '/0-' + filename + '.json', mongoSet, {'urls': arrData},
                 message='Existed ' + str(len(arrData)) + ' for ' + filename)


def doRetrieveAll():
    mongo_log("################START################")

    try:

        doRetrieveTopicList()  # spent 26 min

        doRetrieveTopics()  # spent 15 hours

    except Exception, e:
        mongo_log(str(e), status='error')
        logger.exception(str(e), exc_info=True)

    out_array_data('redirect_urls', redirect_urls, mongo.db.redirect)
    out_array_data('no_replies_urls', no_replies_urls, mongo.db.noreplies)
    out_array_data('empty_urls', empty_urls, mongo.db.empty)

    timeElapsed = datetime.now() - startTime
    mongo_log('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))
    mongo_log("################END################")


def sum_categories():
    result = {}

    topic_num = 0
    posts_num = 0
    pages_num = 0
    for one_category in mongo.db.categories.find():
        topic_num += one_category['topics']
        posts_num += one_category['posts']
        pages_num += one_category['pages']

    result['topics'] = topic_num
    result['posts'] = posts_num
    result['pages'] = pages_num

    return result


def sum_topicslist():
    result = {}

    replies_num = 0
    views_num = 0

    for one_category in mongo.db.categories.find():
        category_id = one_category['category_id']
        category_pages = one_category['pages']

        for category_page in range(1, category_pages + 1):
            # no moved topic
            found_topiclist = mongo.db.topiclist.find(
                {'category_id': category_id, 'category_page': category_page, 'is_moved': 0})
            for one_topic in found_topiclist:
                replies_num += one_topic['replies']
                views_num += one_topic['views']

    result['replies'] = replies_num
    result['views'] = views_num

    return result


def listResults():
    print
    for s in mongo.db.summaries.find():
        print 'Summaries: ' + str(s)
    print 'Categories: ' + str(mongo.db.categories.count())
    print 'TopicList: ' + str(mongo.db.topiclist.count())
    print 'Posts: ' + str(mongo.db.posts.count())
    print 'Replies: ' + str(mongo.db.replies.count())

    categories_num = sum_categories()
    print 'Sum from Categories: ' + str(categories_num)

    topicslist_num = sum_topicslist()
    print 'Sum from TopicsList: ' + str(topicslist_num)

    # for one_post in mongo.db.posts.find({'topic_id': 44962}):  # 44962, 46615, 56861
    #     print one_post
    # for one_post in mongo.db.posts.find({'topic_id': 46615}):  # 44962, 46615, 56861
    #     print one_post
    # for one_post in mongo.db.posts.find({'topic_id': 56861}):  # 44962, 46615, 56861
    #     print one_post

    print


if __name__ == "__main__":
    doRetrieveAll() # spent 15 hours

    listResults()
