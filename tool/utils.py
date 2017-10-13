# -*-coding:utf8-*-
__author__ = 'ggu'

import json
import re


def format_data(data):
    return json.dumps(data, indent=2)


def get_id(data):
    url_ids = re.findall(r"\?id=(\d+)", data)
    id = -1
    if url_ids:
        id = int(url_ids[0])
    return id
