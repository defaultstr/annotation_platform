#!/user/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

try:
    import simplejson as json
except ImportError:
    import json
from collections import defaultdict

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

    p_i = []
    n_j = [0] * len(value_map)

    for query, docno in d:
        values = map(value_map.get, d[(query, docno)])
        n_i = len(values)
        n_ij = [0] * len(value_map)
        for v in values:
            n_ij[v] += 1
            n_j[v] += 1
        p_i.append(1.0 * (sum(map(lambda x: x*x, n_ij)) - n_i) / n_i / (n_i-1))

    P = sum(p_i) / len(p_i)
    p_j = [1.0 * x / sum(n_j) for x in n_j]
    P_e = sum(map(lambda x: x*x, p_j))
    return (P - P_e) / (1 - P_e)


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

    D_o = 0
    for k in d:
        values = d[k]
        D_o += 1.0 / (len(values) - 1) * sum([dist(*x) for x in iter_pairs(values)])
    D_o /= n

    D_e = 1.0 / n / (n - 1) * sum([dist(*x) for x in iter_pairs(all_values)])

    return 1.0 - D_o / D_e
