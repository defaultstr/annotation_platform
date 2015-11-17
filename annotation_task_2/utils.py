#!/user/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

try:
    import simplejson as json
except ImportError:
    import json
from collections import defaultdict
from task_manager.utils import _compute_kappa, _compute_alpha, _compute_weighted_kappa
from task_manager.models import Annotation, Task, TaskUnit 
from sys import stdout


def import_task(topic_num):
    task = Task()
    task.task_name = 'task_2_%s' % topic_num
    task.task_description = '搜索上下文标注-任务:%s' % topic_num
    task.annotation_per_unit = 3
    task.credit_per_annotation = 1
    task.task_tag = 'task_2'
    task.display = True
    return task.save()


def import_task_unit(task, json_str):
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

def get_session(annotation, value):
    jsonObj = json.loads(annotation.annotation_content)
    yield jsonObj['session_id'], value(jsonObj['session_score']) 


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


def compute_weighted_kappa(annotations, extract=get_doc, value=lambda x: int(x)):
    l = []
    for annotation in annotations:
        for k, v in extract(annotation, value):
            l.append((k, annotation.user.username, v))
    return _compute_weighted_kappa(l)



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


def output_annotations(annotations, fout=stdout):
    for annotation in annotations:
        # retrive unit obj
        unit = annotation.task_unit
        unitObj = json.loads(unit.unit_content)
        # delete snippets
        for query in unitObj['queries']:
            for click in query['clicked_docs']:
                del click['snippet']

        annoObj = json.loads(annotation.annotation_content)
        annoObj['task_unit'] = unitObj
        
        print >>fout, json.dumps(annoObj, ensure_ascii=False).encode('utf8')        
        




