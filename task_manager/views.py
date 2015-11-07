#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from django.template import RequestContext

from user_system.utils import *
from .models import *
from .forms import NewTaskForm
from task_manager.settings import tag2controller


def get_task_and_controller(task_id):
    try:
        task = Task.objects.get(id=task_id)
        task_manager = tag2controller[task.task_tag]
        return task, task_manager
    except KeyError:
        return None
    except DoesNotExist:
        return None


@require_login
def list_tasks(user, request):
    tasks = Task.objects(display=True)
    return render_to_response(
        'task_list.html',
        {
            'cur_user': user,
            'tasks': tasks},
        RequestContext(request))


@require_login
def get_next_task_unit(user, request, task_id):
    ret = get_task_and_controller(task_id)
    if ret is None:
        return HttpResponseRedirect('/task/home/')
    task, task_manager = ret

    task_unit = task_manager.get_next_task_unit(user, task)
    if task_unit is not None:
        return HttpResponseRedirect('/task/anno/%s/%s/' % (task_id, task_unit.tag))
    else:
        return HttpResponseRedirect('/task/finished/%s/' % task_id)


@require_login
def finished(user, request, task_id):
    ret = get_task_and_controller(task_id)
    if ret is None:
        return HttpResponseRedirect('/task/home/')
    task, task_manager = ret

    return render_to_response(
        'finished.html',
        {
            'cur_user': user,
            'task': task,
        },
        RequestContext(request)
    )


@require_login
def annotate(user, request, task_id, unit_tag):
    ret = get_task_and_controller(task_id)
    if ret is None:
        return HttpResponseRedirect('/task/home/')
    task, task_manager = ret

    if request.method == 'POST':
        if task_manager.validate_annotation(request, task, unit_tag):
            task_manager.save_annotation(request, task, unit_tag)
            return HttpResponseRedirect('/task/next_task/%s/' % task_id)

    title = u'标注任务-%s-%s' % (task.task_name, unit_tag)
    content = task_manager.get_annotation_content(request, task, unit_tag)
    description = task_manager.get_annotation_description(request, task, unit_tag)
    style = task_manager.get_style(request, task, unit_tag)

    return render_to_response(
        'annotation.html',
        {
            'cur_user': user,
            'title': title,
            'content': content,
            'description': description,
            'style': style
        },
        RequestContext(request)
    )


@require_auth(['admin'])
def manage_tasks(user, request):
    tasks = Task.objects()
    return render_to_response(
        'task_manage_list.html',
        {
            'cur_user': user,
            'tasks': tasks},
        RequestContext(request))


@require_auth(['admin'])
def new_task(user, request):

    form = NewTaskForm()
    error_message = None

    if request.method == 'POST':
        form = NewTaskForm(request.POST)
        if form.is_valid():
            task = Task()
            task.task_name = form.cleaned_data['task_name']
            task.task_description = form.cleaned_data['task_description']
            task.task_tag = form.cleaned_data['task_tag']
            task.annotation_per_unit = 3
            task.credit_per_annotation = 1
            task.display = True
            task.save()
            return HttpResponseRedirect('/task/home/')
        else:
            error_message = form.errors

    return render_to_response(
        'new_task.html',
        {
            'form': form,
            'cur_user': user,
            'error_message': error_message,
        },
        RequestContext(request)
    )


@require_auth(['admin'])
def show_task(user, request, task_id):
    ret = get_task_and_controller(task_id)
    if ret is not None:
        task, task_manager = ret
        task.display = True
        task.save()

    return HttpResponseRedirect('/task/manage/')


@require_auth(['admin'])
def hide_task(user, request, task_id):
    ret = get_task_and_controller(task_id)
    if ret is not None:
        task, task_manager = ret
        task.display = False
        task.save()

    return HttpResponseRedirect('/task/manage/')


@require_auth(['admin'])
def task_info(user, request, task_id):
    ret = get_task_and_controller(task_id)

    if ret is None:
        return HttpResponseRedirect('/task/manage/')

    task, task_manager = ret

    quality_html = '\n'.join(
        ['<p>%s: %f</p>' % (k, v)
            for k, v in task_manager.get_annotation_quality(task).items()]
    )

    return render_to_response(
        'task_info.html',
        {
            'cur_user': user,
            'task': task,
            'task_unit_num': task_manager.get_task_unit_num(task),
            'annotation_num': task_manager.get_annotation_num(task),
            'quality_html': quality_html,
        },
        RequestContext(request),
    )

