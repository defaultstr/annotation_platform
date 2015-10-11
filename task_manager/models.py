#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from mongoengine import *
from user_system.models import User

try:
    import simplejson as json
except ImportError:
    import json


class Task(Document):
    """
    class for a annotation task
    """
    task_name = StringField()             #
    task_description = StringField()      #
    annotation_per_unit = IntField()      #
    credit_per_annotation = IntField()    #
    task_tag = StringField()              # task tag is used for determining corresponding TaskManager


class TaskUnit(Document):
    """
    class for each annotation unit, could be a SERP, a query-url pair, etc.
    """
    tag = StringField(required=True)  # use tag to identify each task unit, should be unique
    unit_content = StringField()      # the content of the task unit, usually a JSON-serialized string
    task = ReferenceField(Task)       # reference to the task


class Annotation(Document):
    """
    class for each annotation made by user
    """
    task_unit = ReferenceField(TaskUnit)  # the corresponding TaskUnit
    user = ReferenceField(User)           # the user that make this annotation
    annotation_content = StringField()    # the annotation data, usually a JSON-serialized string
    task = ReferenceField(Task)           # reference to the task
    credit = IntField()                   # credits per annotation



