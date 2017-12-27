# -*-coding:utf-8-*-
__author__ = 'ggu'

import re

from tool.utils import get_id


def get_user(data):
    return data.string.replace('by', '').strip()


def get_pages(config, uri):
    contents = config.get_bs4request().get_contents(uri)

    for pagepost in contents.findAll('div', class_='pagepost'):
        for pagelink in pagepost.findAll('p', class_='pagelink'):
            # if has next, so try to get the before one
            next_path = get_next_page(contents)
            if next_path:
                next = pagelink.find('a', rel='next', recursive=False)
                siblings = next.findPreviousSiblings('a')
                if siblings:
                    return int(siblings[0].string)
            else:
                strong = pagelink.find('strong')
                if strong:
                    return int(strong.string)

    return 0

def get_next_page(contents):
    for pagepost in contents.findAll('div', class_='pagepost'):
        for pagelink in pagepost.findAll('p', class_='pagelink'):
            next = pagelink.find('a', rel='next', recursive=False)
            if next:
                return next['href']

class TopicList:
    def __init__(self, config):
        self.__config = config

    def get_pages(self, uri):
        return get_pages(self.__config, uri)

    def get_list(self, uri):
        contents = self.__config.get_bs4request().get_contents(uri)
        category_id = get_id(uri)

        # print (uri, category_id)

        results = []

        inbox_table = contents.find('div', id='vf').find('div', class_='inbox')
        for tr in inbox_table.table.tbody.findAll('tr', class_=re.compile('^row(odd|even)$')):
            topic_result = {}
            topic_result['category_id'] = category_id
            results.append(topic_result)

            ismoved = 0
            tr_classes = tr['class']
            if 'imoved' in tr_classes:
                ismoved = 1

            # td
            tdtcl, tdtc2, tdtc3, tdtcr = tr.findAll('td', recursive=False)

            # Topic
            tclcon = tdtcl.find('div', class_='tclcon')
            tclcon_a = tclcon.find('a')
            tclcon_href = tclcon_a['href']
            tclcon_topic = tclcon_a.string

            tclcon_user = get_user(tclcon.find('span', class_='byuser'))

            # print  (tclcon_topic, tclcon_href, tclcon_user)
            topic_result['title'] = tclcon_topic
            topic_result['path'] = tclcon_href
            topic_result['topic_id'] = get_id(tclcon_href)  # topic id from url
            topic_result['reporter'] = tclcon_user

            # Tags
            topiclabels = tdtcl.find('div', class_='topiclabels')
            if topiclabels:
                tags = []
                for tag_a in topiclabels.find('a', recursive=False):
                    tags.append(tag_a.string)

                # print  tags
                topic_result['tags'] = tags

            # if moved, no data
            if ismoved == 0:
                # Replies & Views
                replies_num = int(tdtc2.string.replace(',', ''))
                views_num = int(tdtc3.string.replace(',', ''))

                # print  (replies_num, views_num)
                topic_result['replies'] = replies_num
                topic_result['views'] = views_num

                # Last post
                last_post_datetime = tdtcr.a.string
                last_post_user = get_user(tdtcr.find('span', class_='byuser'))

                # print  (last_post_user, last_post_datetime)
                topic_result['last_post_datetime'] = last_post_datetime
                topic_result['last_post_user'] = last_post_user

        # next page
        # next_path = self.get_next_page(contents)
        # if next_path:
        #     self.get_list(next_path)

        return results




class Topic:
    def __init__(self, config):
        self.__config = config

    def get_pages(self, uri):
        return get_pages(self.__config, uri)

    def get_post(self, uri):
        contents = self.__config.get_bs4request().get_contents(uri)
        topic_post = {}

        firstpost = contents.find('div', id='punviewtopic').find('div', class_='firstpost')
        if firstpost:
            postdate = firstpost.h2.span.a.string
            floor = int(firstpost.h2.span.span.string.replace('#', '').strip())
            topic_post['post_date'] = postdate
            topic_post['floor'] = floor

            postbody = firstpost.find('div', class_='postbody')
            # TODO

    def get_replies(self, uri):
        contents = self.__config.get_bs4request().get_contents(uri)


if __name__ == "__main__":
    from config import Config
    from datetime import datetime

    startTime = datetime.now()

    config = Config()

    # list
    topicList = TopicList(config)
    uri = 'viewforum.php?id=13'  # 13=(3,65) 35=(69,2065)
    pages = topicList.get_pages(uri)
    results = topicList.get_list(uri)

    print (pages, len(results))

    # topic contents
    topic = Topic(config)
    t_uri = 'viewtopic.php?id=48691'
    t_pages = topic.get_pages(t_uri)
    t_post = topic.get_post(t_uri)
    t_replies = topic.get_replies(t_uri)

    print (t_pages, len(t_replies))

    timeElapsed = datetime.now() - startTime
    print('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))
