#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from django.template import loader, RequestContext
from task_manager.models import *
from task_manager.controllers import TaskManager
from user_system.utils import *

try:
    import simplejson as json
except ImportError:
    import json


class QueryDocumentTaskManager(TaskManager):
    """
    TaskManager for query-document pair annotation
    """
    def get_annotation_content(self, request, task, unit_tag):
        """
        :param task: task
        :param unit_tag:
        :return: Html fragment that will be inserted to the content block.
        """
        try:
            task_unit = TaskUnit.objects.get(task=task, tag=unit_tag)
            jsonObj = json.loads(task_unit.unit_content)
            t = loader.get_template('annotation_task_1_content.html')
            c = RequestContext(
                request,
                {
                    'query': jsonObj['query'],
                    'html': jsonObj['doc_snippet'],
                })
            return t.render(c)
        except DoesNotExist:
            return '<div>Error! Can\'t find task unit!</div>'

    def get_annotation_description(self, request, task, unit_tag):
        """
        :param task:
        :param unit_tag:
        :return: Html fragment that will be inserted to the description block
        """
        user = get_user_from_request(request)
        finished_task_num = len(Annotation.objects(user=user, task=task))
        all_task_num = len(TaskUnit.objects(task=task))
        t = loader.get_template('annotation_task_1_description.html')
        c = RequestContext(
            request,
            {
                'task_name': task.task_name,
                'task_description': task.task_description,
                'finished_unit_num': finished_task_num,
                'all_unit_num': all_task_num,
            }
        )
        return t.render(c)

    def get_style(self, request, task, unit_tag):
        """
        :param task:
        :param unit_tag:
        :return: CSS fragment that will be inserted to the css block
        """
        t = loader.get_template('annoation_task_1.css')
        c = RequestContext(
            request, {}
        )
        return t.render(c)

