__author__ = 'zzitaI'

from task_manager.models import *
from task_manager.controllers import TaskManager
from user_system.utils import *

try:
    import simplejson as json
except ImportError:
    import json


class SessionTaskManager(TaskManager):
    pass
