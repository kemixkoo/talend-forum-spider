# -*-coding:utf-8-*-
__author__ = 'ggu'

import re
import frequest


def getuser(data):
    return data.string.replace('by', '').strip()


class TopicList:
    def __init__(self, path):
        bs4request = frequest.BS4Request(path)
        self.__contents = bs4request.contents
        self.url = bs4request.url

        self.pages = self.getpages()
        self.list = self.getlist()

    def getpages(self):
        for pagepost in self.__contents.findAll('div', class_='pagepost'):
            for pagelink in pagepost.findAll('p', class_='pagelink'):
                # if has next, so try to get the before one
                next_path = self.getnextpage()
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

    def getlist(self):
        results = []

        inbox_table = self.__contents.find('div', id='vf').find('div', class_='inbox')
        for tr in inbox_table.table.tbody.findAll('tr', class_=re.compile('^row(odd|even)$')):
            topic_result = {}
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

            tclcon_user = getuser(tclcon.find('span', class_='byuser'))

            # print  (tclcon_topic, tclcon_href, tclcon_user)
            topic_result['title'] = tclcon_topic
            topic_result['path'] = tclcon_href
            # topic_result['topic_id'] = tclcon_href.substring('?id=')
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
                last_post_user = getuser(tdtcr.find('span', class_='byuser'))

                # print  (last_post_user, last_post_datetime)
                topic_result['last_post_datetime'] = last_post_datetime
                topic_result['last_post_user'] = last_post_user

        # next page
        next_path = self.getnextpage()
        if next_path:
            results.extend(TopicList(next_path).list)

        return results

    def getnextpage(self):
        for pagepost in self.__contents.findAll('div', class_='pagepost'):
            for pagelink in pagepost.findAll('p', class_='pagelink'):
                next = pagelink.find('a', rel='next', recursive=False)
                if next:
                    return next['href']


class Topic:
    def __init__(self, path):
        bs4request = frequest.BS4Request(path)
        self.__contents = bs4request.contents
        self.url = bs4request.url

    def getq(self):
        self.__contents.findAll('div')

    def getreplies(self):
        self.__contents.findAll('div')


if __name__ == "__main__":
    # Index >> Data Quality - Non technical discussions
    topicList = TopicList('viewforum.php?id=13')
    print (topicList.pages, len(topicList.list))
