#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from django.template import loader, RequestContext
from django import forms
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

    def get_next_task_unit(self, user, task):
        """
        The default schedule method just returns next task unit that the user has not annotated.
        :param user: user
        :param task: task
        :return: next task unit, None if no new task needs annotation
        """

        task_units = TaskUnit.objects(task=task)
        task_units = sorted(task_units, key=lambda x: json.loads(x.unit_content)['url'])
        task_unit_tags = [t.tag for t in task_units]

        annotations = Annotation.objects(task=task, user=user)
        annotated_tags = set([a.task_unit.tag for a in annotations])

        for tag in task_unit_tags:
            if tag in annotated_tags:
                continue
            else:
                return TaskUnit.objects(task=task, tag=tag)[0]

        return None

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
                    'task_id': task.id,
                    'unit_tag': unit_tag,
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

    def validate_annotation(self, request, task, unit_tag):
        try:
            unit_tag = request.POST['unit_tag']
            task_id = request.POST['task_id']
            score = int(request.POST['score'])
            my_task = Task.objects.get(id=task_id)
            if task != my_task:
                return False
            task_unit = TaskUnit.objects.get(task=task, tag=unit_tag)
            return True
        except KeyError:
            return False
        except DoesNotExist:
            return False
        except ValueError:
            return False

    def save_annotation(self, request, task, unit_tag):
        try:
            task_unit = TaskUnit.objects.get(task=task, tag=unit_tag)
            user = get_user_from_request(request)
            score = int(request.POST['score'])
            a = Annotation()
            a.user = user
            a.task_unit = task_unit
            a.annotation_content = json.dumps({'score': score})
            a.task = task
            a.credit = task.credit_per_annotation
            a.save()
        except DoesNotExist:
            return None
        except ValueError:
            return None

