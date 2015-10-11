#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from .models import *
try:
    import simplejson as json
except ImportError:
    import json


def import_task(task_name,
                task_description,
                annotation_per_unit = 3,
                credit_per_annotation = 1):
    t = Task()
    t.task_name = task_name
    t.task_description = task_description
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



