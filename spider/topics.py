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

        h_punviewtopic = contents.find('div', id='punviewtopic')
        if h_punviewtopic:
            h_firstpost = h_punviewtopic.find('div', class_='firstpost')
            if h_firstpost:
                return get_post_results(h_firstpost)

    def get_replies(self, uri):
        contents = self.__config.get_bs4request().get_contents(uri)
        replies = []
        h_punviewtopic = contents.find('div', id='punviewtopic')
        if h_punviewtopic:
            h_blockpost = h_punviewtopic.findAll('div', class_='blockpost')
            if h_blockpost:
                for h_each_blockpost in h_blockpost:
                    if 'firstpost' not in h_each_blockpost['class']:
                        replies.append(get_post_results(h_each_blockpost))
        return replies


def get_post_results(h_blockpost):
    post_details = {}
    postdate = h_blockpost.h2.span.a.string
    floor = int(h_blockpost.h2.span.span.string.replace('#', '').strip())
    post_details['post_date'] = postdate
    post_details['floor'] = floor

    h_postbody = h_blockpost.find('div', class_='postbody')

    # user
    h_postleft = h_postbody.find('div', class_='postleft')
    h_a_reporter = h_postleft.dl.dt.strong
    reporter = h_a_reporter.string
    post_details['reporter'] = reporter
    if h_a_reporter.a:
        reporter_uri = h_a_reporter.a['href']
        post_details['reporter_uri'] = reporter_uri

    # type
    h_usertitle = h_postleft.dl.find('dd', class_='usertitle')
    reporter_type = h_usertitle.strong.string
    post_details['type'] = reporter_type

    # avatar pic
    h_postavatar = h_postleft.dl.find('dd', class_='postavatar')
    if h_postavatar:
        avatar_uri = h_postavatar.img['src']
        post_details['avatar_uri'] = avatar_uri

    # 26 posts
    h_postnum = h_usertitle.next_sibling
    if h_postnum:
        post_num = h_postnum.string
        if post_num.endswith(' posts'):
            post_num = post_num[:-6]
        if post_num.endswith(' post'):
            post_num = '1'
        if '\n' not in post_num:
            post_details['posts'] = int(post_num)

    # stars
    h_karma = h_postleft.dl.find('p', class_='karma')
    if h_karma:
        h_stars = h_karma.findAll('img', src='img/icon_star.png')
        if h_stars:
            post_details['stars'] = len(h_stars)

    # title
    h_postright = h_postbody.find('div', class_='postright')
    title = unicode(h_postright.h3.string)
    post_details['title'] = title
    # status
    if title.startswith('[resolved]'):
        post_details['status'] = 'resolved'

    # messages
    h_postmsg = h_postright.find('div', class_='postmsg')
    messges = unicode(h_postmsg.get_text())
    post_details['messges'] = messges

    # tags
    labels = []
    h_topiclabels = h_postmsg.findAll('div', class_='topiclabels')
    if h_topiclabels:
        for h_tl in h_topiclabels:
            for h_a in h_tl.findAll('a'):
                tag = h_a.string
                labels.append(tag)
    if len(labels) > 0:
        post_details['tags'] = labels

    # attached img
    postimgs = []
    for h_postimg in h_postmsg.findAll('a', class_='postimg'):
        src = h_postimg.img['src']
        postimgs.append(src)
    if len(postimgs) > 0:
        post_details['images'] = postimgs

    # post signature
    h_postsignature = h_postright.find('div', class_='postsignature')
    if h_postsignature:
        signature = unicode(h_postsignature.get_text())
        post_details['signature_contents'] = signature
        h_sigimage = h_postsignature.findAll('img', class_='sigimage')
        if h_sigimage:
            sigimgs = []
            for h_each_sigimage in h_sigimage:
                sigimgs.append(h_each_sigimage['src'])
            if len(sigimgs) > 0:
                post_details['signature_images'] = sigimgs

    return post_details


if __name__ == "__main__":
    from conf.config import Config
    from datetime import datetime

    startTime = datetime.now()

    config = Config()

    # list
    # topicList = TopicList(config)
    # uri = 'viewforum.php?id=13'  # 13=(3,65) 35=(69,2065)
    # pages = topicList.get_pages(uri)
    # results = topicList.get_list(uri)
    # print (pages, len(results))

    # topic contents
    topic = Topic(config)

    # with Guest: 26137, more pages+tags+signature img:55245
    #  redirect:31747 will be null post, [] for replies
    t_uri = 'viewtopic.php?id=55245'
    t_pages = topic.get_pages(t_uri)
    t_post = topic.get_post(t_uri)
    t_replies = topic.get_replies(t_uri)

    print t_pages

    import tool.utils

    print tool.utils.format_data(t_post)
    print tool.utils.format_data(t_replies)

    timeElapsed = datetime.now() - startTime
    print('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))
