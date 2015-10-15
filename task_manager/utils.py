#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from collections import defaultdict
from .models import *
try:
    import simplejson as json
except ImportError:
    import json


def import_task(task_name,
                task_description,
                task_tag,
                annotation_per_unit = 3,
                credit_per_annotation = 1):
    t = Task()
    t.task_name = task_name
    t.task_description = task_description
    t.task_tag = task_tag
    t.annotation_per_unit = annotation_per_unit
    t.credit_per_annotation = credit_per_annotation
    t.save()
    return t


def import_task_unit(task, json_str):
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


def compute_kappa(annotations, key=get_query_doc_pair, value=get_query_doc_score):
    annotations = list(annotations)

    value_set = set()
    for a in annotations:
        value_set.add(get_query_doc_score(a))

    value_map = {v: i for i, v in enumerate(sorted(value_set))}

    d = defaultdict(list)
    for a in annotations:
        query, docno = get_query_doc_pair(a)
        d[(query, docno)].append(get_query_doc_score(a))

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