# -*- coding:utf-8 -*-
__author__ = 'ggu'

import re

from tool.utils import save_to_file, find_id, get_uri_pages


class Category:
    def __init__(self, config):
        self.__config = config
        self.__contents = self.__config.get_bs4request().get_contents()

        self.stats = self.get_stats()
        self.details = self.get_details()

    def get_stats(self):
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

    def get_details(self):
        results = []

        for blocktable in self.__contents.findAll(id=re.compile("^idx\d+$"), class_='blocktable'):
            top_title = blocktable.h2.span.string

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

                # pages
                pages = get_uri_pages(self.__config, sub_url)

                # sub result
                subresult = {}

                subresult['top_title'] = top_title
                subresult['title'] = sub_title
                subresult['desc'] = sub_title_desc
                subresult['path'] = sub_url
                subresult['category_id'] = find_id(sub_url)
                subresult['pages'] = pages
                subresult['topics'] = topics_num
                subresult['posts'] = posts_num
                subresult['talenders'] = talenders
                subresult['last_modified_datatime'] = last_modified_datetime

                results.append(subresult)

        return results


if __name__ == "__main__":
    from conf.config import Config
    import timeit

    start = timeit.default_timer()
    config = Config()
    category = Category(config)

    # print format_data(category.stats)
    # print "-------------------------------------"
    # print format_data(category.details)

    print category.stats
    print category.details

    result_folder = config['spider.result_folder']
    save_to_file(result_folder + '/categories-stats', category.stats)
    save_to_file(result_folder + '/categories-details', category.details)

    end = timeit.default_timer()
    print "spend: %i s" % (end - start)
