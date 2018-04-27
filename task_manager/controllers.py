#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from user_system.models import *
from .models import *
from .utils import send_task_finished_email


class TaskManager(object):
    """
    A controller class which provides default implement for the function needed in views.py

    Ideally, a new type of annotation task can be integrated into the system
    by subclassing TaskManager class, and put right content in TaskUnit document
    """

    def get_next_task_unit(self, request, user, task):
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

    def get_task_unit_num(self, task):
        """
        Return the number of task units of given task
        :param task:
        :return: number of task units
        """
        return len(TaskUnit.objects(task=task))

    def get_annotation_num(self, task):
        """
        Return the number of annotations corresponding to given task
        :param task:
        :return: number of annotations
        """
        return len(Annotation.objects(task=task))

    def get_annotation_quality(self, task):
        """
        Return a dict of quality metrics
        :param task:
        :return: a dict of implemented quality metrics like kappa or alpha
        """
        return {}

    def send_task_finished_emails(self, request, task, user, admin_emails=[]):
        """
        send emails to admins, when an annotator finishs all the task unit in a task.
        :param user:
        :param task:
        :return:
        """
        send_task_finished_email(request,
                                 task,
                                 user,
                                 self.get_task_info_html(task),
                                 admin_emails=admin_emails)


    def get_task_info_html(self, task):
        """
        return brief information about current task
        :param task:
        :return: info string
        """
        return ''

