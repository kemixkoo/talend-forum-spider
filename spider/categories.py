# -*- coding:utf-8 -*-
__author__ = 'ggu'

import re
from  forum.frequest import BS4Request


class Category:
    def __init__(self):
        self.__contents = BS4Request().contents

        self.stats = self.getstats()
        self.details = self.getdetails()

    def getstats(self):
        brdstats_conr = self.__contents.find('div', id='brdstats', class_='block').find('dl', class_='conr')
        brdstats_dd = brdstats_conr.findAll('dd', recursive=False)
        total_registered_users = int(brdstats_dd[0].span.strong.string.replace(',', ''))
        total_topics = int(brdstats_dd[1].span.strong.string.replace(',', ''))
        total_posts = int(brdstats_dd[2].span.strong.string.replace(',', ''))

        # print(total_registered_users, total_topics, total_posts)

        results = {}
        results['registered_users'] = total_registered_users
        results['topics'] = total_topics
        results['posts'] = total_posts
        return results

    def getdetails(self):
        results = {}

        for blocktable in self.__contents.findAll(id=re.compile("^idx\d+$"), class_='blocktable'):
            top_title = blocktable.h2.span.string
            results[top_title] = {}

            for tr in blocktable.table.findAll('tr', class_=re.compile('^row(odd|even)$')):
                tdtc1, tdtc2, tdtc3, tdtcr = tr.findAll('td', recursive=False)

                # topics and posts
                topics_num = int(tdtc2.string.replace(',', ''))
                posts_num = int(tdtc3.string.replace(',', ''))

                # sub category
                tclcon = tdtc1.find('div', class_='tclcon')

                h3_a = tclcon.find('h3').a
                sub_title = h3_a.string
                sub_url = h3_a['href']

                # description
                forumdesc = tclcon.find('div', class_='forumdesc')
                sub_title_desc = forumdesc.string

                modlist = tclcon.find('p', class_='modlist')
                talenders = []
                if modlist:
                    for modlist_a in modlist.findAll('a'):
                        talenders.append(modlist_a.string)

                # Last post
                last_modified_datetime = tdtcr.a.string

                # sub result
                subresult = {}
                results[top_title][sub_title] = subresult

                subresult['desc'] = sub_title_desc
                subresult['path'] = sub_url
                subresult['topics'] = topics_num
                subresult['posts'] = posts_num
                subresult['talenders'] = talenders
                subresult['last_modified_datatime'] = last_modified_datetime

        return results


if __name__ == "__main__":
    category = Category()
    print category.stats
    print category.details
