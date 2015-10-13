#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from user_system.models import *
from .models import *


class TaskManager(object):
    """
    A controller class which provides default implement for the function needed in views.py

    Ideally, a new type of annotation task can be integrated into the system
    by subclassing TaskManager class, and put right content in TaskUnit document
    """

    def get_next_task_unit(self, user, task):
        """
        The default schedule method just returns next task unit that the user has not annotated.
        :param user: user
        :param task: task
        :return: next task unit, None if no new task needs annotation
        """

        task_units = TaskUnit.objects(task=task)
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
        return '<div>Test content! get_annotation_content method should be override!</div>'

    def get_annotation_description(self, request, task, unit_tag):
        """
        :param task:
        :param unit_tag:
        :return: Html fragment that will be inserted to the description block
        """
        return '<div class="test_style">Test description! get_annotation_description method should be override!</div>'

    def get_style(self, request, task, unit_tag):
        """
        :param task:
        :param unit_tag:
        :return: CSS fragment that will be inserted to the css block
        """
        return '.test_style { font-size: smaller}'

    def validate_annotation(self, request, task, unit_tag):
        """
        Validate the annotation request for given task and task unit.
        TODO: use exception to let view know what is wrong.
        :param request:
        :param task:
        :param unit_tag:
        :return: True if the request is a valid annotation, False otherwise
        """
        return False

    def save_annotation(self, request, task, unit_tag):
        """
        Save annotation in database
        :param request:
        :param task:
        :param unit_tag:
        :return: Annotation object
        """

        return None

