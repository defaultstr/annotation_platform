#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

import math
from collections import defaultdict
from .models import *
try:
    import simplejson as json
except ImportError:
    import json
from django.core.mail import EmailMultiAlternatives
import smtplib
import numpy as np


def _compute_weighted_kappa(l):
    """
    :param l:  an (item, annotator, label)-triplet list, labels must be ordinal
    :return: weighted kappa
    """
    # get value map
    value_list = [int(x[2]) for x in l]
    max_label = max(value_list)
    min_label = min(value_list)
    value_map = {x: i for i, x in enumerate(range(min_label, max_label+1))}

    # weighted function
    def weight(x, y):
        return 1.0 - 1.0 * abs(x - y) / (max_label - min_label)

    # compute marginal prob. of each annotator
    n_j = defaultdict(lambda: [0] * len(value_map))
    for _, annotator, label in l:
        x = value_map[label]
        n_j[annotator][x] += 1

    for annotator in n_j:
        normalizer = 1.0 * sum(n_j[annotator])
        for x in range(len(value_map)):
            n_j[annotator][x] /= normalizer

    # group triplets by item
    d = defaultdict(list)
    for item, annotator, label in l:
        d[item].append((annotator, label))

    # compute kappa
    kappas = []
    for item in d:
        for i in range(len(d[item])):
            for j in range(i+1, len(d[item])):
                x = value_map[d[item][i][1]]
                anno_x = d[item][i][0]
                y = value_map[d[item][j][1]]
                anno_y = d[item][j][0]
                p_o = weight(x, y)

                p_e = 0.0
                for x in range(len(value_map)):
                    for y in range(len(value_map)):
                        p_e += weight(x, y) * n_j[anno_x][x] * n_j[anno_y][y]

                kappas.append((p_o - p_e) / (1.0 - p_e))

    return sum(kappas) / len(kappas), np.std(kappas) / np.sqrt(len(kappas))


def _compute_kappa(d, value_map):
    p_i = []
    n_j = [0] * len(value_map)

    for k in d:
        if len(d[k]) < 2:
            continue
        values = map(value_map.get, d[k])
        n_i = len(values)
        n_ij = [0] * len(value_map)
        for v in values:
            n_ij[v] += 1
            n_j[v] += 1
        p_i.append(1.0 * (sum(map(lambda x: x*x, n_ij)) - n_i) / n_i / (n_i-1))

    P = sum(p_i) / len(p_i)
    p_j = [1.0 * x / sum(n_j) for x in n_j]
    P_e = sum(map(lambda x: x*x, p_j))
    if P_e == 1.0:
        return 1.0
    else:
        return (P - P_e) / (1 - P_e)


def _compute_alpha(n, d, all_values):
    def iter_pairs(l):
        size = len(l)
        if size >= 2:
            for i in range(size-1):
                for j in range(i+1, size):
                    yield l[i], l[j]

    def dist(x, y):
        return (x - y) * (x - y)

    D_o = 0
    for k in d:
        values = d[k]
        if len(values) < 2:
            continue
        D_o += 1.0 / (len(values) - 1) * sum([dist(*x) for x in iter_pairs(values)])
    D_o /= n

    D_e = 1.0 / n / (n - 1) * sum([dist(*x) for x in iter_pairs(all_values)])

    return 1.0 - D_o / D_e


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


def import_task_and_task_units(task_name, task_description, task_tag, path,
                               annotation_per_unit=3, credit_per_annotation=1):
    t = import_task(task_name, task_description, task_tag)
    batch_import_task_units_from_file(t, path)


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


def send_task_finished_email(request, task, user, task_info, admin_emails=[]):
    subject = u'THUIR标注平台任务完成'

    message = u'用户%s ' % user.username

    message += u'已完成任务%s: %s的标注.</br>' % (task.task_name, task.task_description)
    message += task_info + '</br>'
    message += u'任务详情,请点击：'
    host = u'http://' + request.get_host()
    url = unicode(host + '/task/info/%s/' % task.id)
    html_content = message + u'<a href="%s">%s</a>.' % (url, url)
    message += url

    source = 'thuir_annotation@163.com'
    for target in admin_emails:
        msg = EmailMultiAlternatives(subject, message, source, [target])
        msg.attach_alternative(html_content, 'text/html')
        try:
            msg.send()
        except smtplib.SMTPException as e:
            print type(e)
            print e

