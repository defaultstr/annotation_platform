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
    u.tag = str(obj['docno'])
    u.unit_content = json_str
    u.save()
    return u


def batch_import_task_units_from_file(task, path):
    with open(path, 'r') as fin:
        for line in fin:
            import_task_unit(task, line)

def get_query_doc_pair(annotation):
    obj = json.loads(annotation.annotation_content)
    return obj['query'], obj['docno']


def get_query_doc_score(annotation):
    obj = json.loads(annotation.annotation_content)
    return obj['score']


def get_two_level_doc_score(annotation):
    obj = json.loads(annotation.annotation_content)
    return 0 if obj['score'] <= 2 else 1


def output_annotations(annotations, key=get_query_doc_pair, value=get_query_doc_score):
    annotations = list(annotations)

    d = defaultdict(list)
    for a in annotations:
        k = key(a)
        d[k].append(value(a))

    for k in d:
        query, docno = k
        values = sorted(d[k])
        yield query, docno, values[len(values)/2]


def compute_kappa(annotations, key=get_query_doc_pair, value=get_query_doc_score):
    annotations = list(annotations)

    value_set = set()
    for a in annotations:
        value_set.add(value(a))

    value_map = {v: i for i, v in enumerate(sorted(value_set))}

    d = defaultdict(list)
    for a in annotations:
        query, docno = key(a)
        d[(query, docno)].append(value(a))

    return _compute_kappa(d, value_map)


def compute_alpha(annotations, key=get_query_doc_pair, value=get_query_doc_score):

    def iter_pairs(l):
        size = len(l)
        if size >= 2:
            for i in range(size-1):
                for j in range(i+1, size):
                    yield l[i], l[j]

    def dist(x, y):
        return (x - y) * (x - y)

    annotations = list(annotations)

    n = 0
    d = defaultdict(list)
    all_values = []
    for a in annotations:
        query, docno = key(a)
        d[(query, docno)].append(value(a))
        all_values.append(value(a))
        n += 1
    return _compute_alpha(n, d, all_values)


