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


def get_user(data):
    return data.string.replace('by', '').strip()


def get_uri_pages(config, uri):
    contents = config.get_bs4request().get_contents(uri)
    return get_pages(contents)


def get_pages(contents):
    if contents is None:
        return

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


def get_next_page(contents):
    for pagepost in contents.findAll('div', class_='pagepost'):
        for pagelink in pagepost.findAll('p', class_='pagelink'):
            next = pagelink.find('a', rel='next', recursive=False)
            if next:
                return next['href']


def get_target_files():
    return split(realpath(__file__))[0] + '/../target/files'


def save_to_file(file, data):
    if not file:
        return

    target_files = get_target_files()
    if not str(file).startswith('/'):
        file = target_files + '/' + file

    files = split(file)
    parent_folder = files[0]
    if not exists(parent_folder):
        makedirs(parent_folder)

    if '.' not in files[1]:
        file = file + '.json'

    fo = open(file, 'w')

    value = format_data(data)
    fo.write(value)
