__author__ = 'zzitaI'

from django.template import loader, RequestContext
from django import forms
from task_manager.models import *
from task_manager.controllers import TaskManager
from user_system.utils import *
from .utils import *

try:
    import simplejson as json
except ImportError:
    import json


class SessionTaskManager(TaskManager):
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

        '''
        import random
        return TaskUnit.objects(task=task, tag=random.choice(task_unit_tags))[0]
        '''

    def get_annotation_content(self, request, task, unit_tag):
        """
        :param task: task
        :param unit_tag:
        :return: Html fragment that will be inserted to the content block.
        """
        try:
            task_unit = TaskUnit.objects.get(task=task, tag=unit_tag)
            jsonObj = json.loads(task_unit.unit_content)

            # generate queries
            queries = []
            for idx, q in enumerate(jsonObj['queries']):
                # generate clicked docs
                clicked_docs = []
                for d in q['clicked_docs']:
                    t = loader.get_template('annotation_task_2_doc.html')
                    c = RequestContext(
                        request,
                        {
                            'html': d['snippet'],
                            'doc_id': d['id'],
                            'dwell_time': format_time(d['dwell_time']),
                            'rank': d['rank'] + 1,
                        }
                    )
                    clicked_docs.append(t.render(c))

                t = loader.get_template('annotation_task_2_query.html')
                c = RequestContext(
                    request,
                    {
                        'query': q['query'],
                        'query_index': idx + 1,
                        'task_id': task.id,
                        'query_id': q['id'],
                        'query_time': format_time(q['dwell_time']),
                        'clicked_docs': clicked_docs,
                    }
                )
                queries.append(t.render(c))

            t = loader.get_template('annotation_task_2_content.html')
            c = RequestContext(
                request,
                {
                    'task_id': task.id,
                    'session_id': jsonObj['id'],
                    'queries': queries,
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
        task_unit = TaskUnit.objects(task=task, tag=unit_tag)[0]
        task_desc = json.loads(task_unit.unit_content)['topic_desc']

        all_task_num = len(TaskUnit.objects(task=task))
        t = loader.get_template('annotation_task_2_description.html')
        c = RequestContext(
            request,
            {
                'task_name': task.task_name,
                'task_description': task_desc,
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
        t = loader.get_template('annotation_task_2.css')
        c = RequestContext(
            request, {}
        )
        return t.render(c)

    def validate_annotation(self, request, task, unit_tag):

        json_str = request.POST['message']
        jsonObj = json.loads(json_str)
        print json.dumps(jsonObj, sort_keys=True, indent=4)
        try:
            # check task id
            task_id = jsonObj['task_id']
            my_task = Task.objects.get(id=task_id)
            if my_task != task:
                return False

            if jsonObj['session_id'] != unit_tag:
                return False
            task_unit = TaskUnit.objects.get(task=task, tag=unit_tag)
        except KeyError:
            return False
        except DoesNotExist:
            return False
        except ValueError:
            return False

        return True

    def save_annotation(self, request, task, unit_tag):
        try:
            task_unit = TaskUnit.objects.get(task=task, tag=unit_tag)
            user = get_user_from_request(request)
            a = Annotation()
            a.user = user
            a.task_unit = task_unit

            jsonObj = json.loads(request.POST['message'])
            jsonObj['annotator'] = user.username
            a.annotation_content = json.dumps(jsonObj, ensure_ascii=False)

            a.task = task
            a.credit = task.credit_per_annotation
            a.save()
        except DoesNotExist:
            return None
        except ValueError:
            return None

    def get_annotation_quality(self, task):
        annotations = list(Annotation.objects(task=task))
        ret = {}

        if len(annotations) == 0:
            return ret

        ret['doc 4-level kappa'] = compute_kappa(annotations)
        ret['doc weighted kappa'] = compute_weighted_kappa(annotations)
        ret['doc alpha'] = compute_alpha(annotations)

        ret['query 4-level kappa'] = compute_kappa(annotations, extract=get_query)
        ret['query weighte kappa'] = compute_weighted_kappa(annotations, extract=get_query)
        ret['query alpha'] = compute_alpha(annotations, extract=get_query)

        return ret
