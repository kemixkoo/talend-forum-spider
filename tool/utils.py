# -*-coding:utf8-*-
__author__ = 'ggu'

import json
import re
from os import makedirs
from os.path import realpath, split, exists


def format_data(data):
    return json.dumps(data, indent=2)


def get_viewforum_uri(category_id, page=1):
    if page > 1:
        return 'viewforum.php?id=' + str(category_id) + '&p=' + str(page)
    else:
        return 'viewforum.php?id=' + str(category_id)


def get_viewtopic_uri(topic_id, page=1):
    if page > 1:
        return 'viewtopic.php?id=' + str(topic_id) + '&p=' + str(page)
    else:
        return 'viewtopic.php?id=' + str(topic_id)


def get_id(data):
    url_ids = re.findall(r"\?id=(\d+)", data)
    id = -1
    if url_ids:
        id = int(url_ids[0])
    return id


def get_page(data):
    url_pages = re.findall(r"\&p=(\d+)", data)
    id = 1  # even the first one is not in url
    if url_pages:
        id = int(url_pages[0])
    return id


def get_target_files():
    return split(realpath(__file__))[0] + '/../target/files'


def save_to_file(filename, data):
    target_files = get_target_files()
    if not exists(target_files):
        makedirs(target_files)

    file = target_files + '/' + filename
    fo = open(file, 'w')

    value = format_data(data)
    fo.write(value)
