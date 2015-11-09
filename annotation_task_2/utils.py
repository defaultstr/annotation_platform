#!/user/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

try:
    import simplejson as json
except ImportError:
    import json
from collections import defaultdict
from task_manager.utils import _compute_kappa, _compute_alpha


def import_task_unit(task, json_str):
    from task_manager.models import *
    obj = json.loads(json_str)
    u = TaskUnit()
    u.task = task
    u.tag = str(obj['id'])
    u.unit_content = json_str
    u.save()
    return u


def batch_import_task_units_from_file(task, path):
    with open(path, 'r') as fin:
        for line in fin:
            import_task_unit(task, line)


def format_time(sec):
    minute = int(sec / 60.0)
    if minute == 0:
        minute = ''
    else:
        minute = '%dmin' % minute
    sec %= 60.0
    return minute + ('%.1fsec' % sec)


def get_two_level(x):
    x = int(x)
    return 0 if x <= 2 else 1


def get_doc(annotation, value):
    jsonObj = json.loads(annotation.annotation_content)
    for doc in jsonObj['doc_annotations']:
        yield doc['doc_id'], value(doc['doc_score'])


def get_query(annotation, value):
    jsonObj = json.loads(annotation.annotation_content)
    for query in jsonObj['query_annotations']:
        yield query['query_id'], value(query['query_score'])


def compute_kappa(annotations, extract=get_doc, value=lambda x:int(x)):
    value_set = set()
    for annotation in annotations:
        for _, v in extract(annotation, value):
            value_set.add(v)
    value_map = {v: i for i, v in enumerate(sorted(value_set))}

    d = defaultdict(list)
    for annotation in annotations:
        for k, v in extract(annotation, value):
            d[k].append(v)

    return _compute_kappa(d, value_map)


def compute_alpha(annotations, extract=get_doc, value=lambda x:int(x)):
    n = 0
    d = defaultdict(list)
    all_values = []

    d = defaultdict(list)
    for a in annotations:
        for k, v in extract(a, value):
            d[k].append(v)
            all_values.append(v)
            n += 1
    return _compute_alpha(n, d, all_values)




