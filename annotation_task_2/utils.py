#!/user/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'


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

