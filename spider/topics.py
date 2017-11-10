# -*-coding:utf-8-*-
__author__ = 'ggu'

import re
from forum.tool.utils import get_id, get_page, save_to_file


def get_user(data):
    return data.string.replace('by', '').strip()


class TopicList:
    def __init__(self, config):
        self.__config = config

    def get_pages(self, uri):
        contents = self.__config.get_bs4request().get_contents(uri)

        for pagepost in contents.findAll('div', class_='pagepost'):
            for pagelink in pagepost.findAll('p', class_='pagelink'):
                # if has next, so try to get the before one
                next_path = self.get_next_page(contents)
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

        # save to file
        current_page = get_page(uri)
        current_file = "topics-" + str(category_id) + "-" + str(current_page)
        save_to_file(current_file, results)

        # next page
        next_path = self.get_next_page(contents)
        if next_path:
            self.get_list(next_path)

        return results

    def get_next_page(self, contents):
        for pagepost in contents.findAll('div', class_='pagepost'):
            for pagelink in pagepost.findAll('p', class_='pagelink'):
                next = pagelink.find('a', rel='next', recursive=False)
                if next:
                    return next['href']


class Topic:
    def __init__(self, config, uri):
        self.__config = config
        self.__uri = uri
        self.url = self.__config['url'] + self.__uri

    def get_post(self):
        contents = self.__config.get_bs4request().get_contents(self.__uri)

    def get_replies(self, uri):
        contents = self.__config.get_bs4request().get_contents(uri)


if __name__ == "__main__":
    from forum.config import Config
    import timeit

    start = timeit.default_timer()

    # Index >> Data Quality - Non technical discussions
    topicList = TopicList(Config())

    uri = 'viewforum.php?id=13'  # 13=(3,65) 35=(69,2065)
    pages = topicList.get_pages(uri)
    results = topicList.get_list(uri)

    print (pages, len(results))

    end = timeit.default_timer()
    print "spend: %i s" % (end - start)
