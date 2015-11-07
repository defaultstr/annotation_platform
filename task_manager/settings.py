#!/user/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from annotation_task_1.controllers import QueryDocumentTaskManager
from annotation_task_2.controllers import SessionTaskManager

tag2controller = {
    'task_1': QueryDocumentTaskManager(),
    'task_2': SessionTaskManager(),
}

