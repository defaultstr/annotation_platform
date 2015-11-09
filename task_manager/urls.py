#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = [
    url(r'^home/$', views.list_tasks),
    url(r'^finished/([0-9a-z]+)/$', views.finished),
    url(r'^next_task/([0-9a-z]+)/$', views.get_next_task_unit),
    url(r'^anno/([0-9a-z]+)/(\w+)/', views.annotate),

    # task manager
    url(r'^manage/$', views.manage_tasks),
    url(r'^new/$', views.new_task),
    url(r'^show/([0-9a-z]+)/$', views.show_task),
    url(r'^hide/([0-9a-z]+)/$', views.hide_task),
    url(r'^info/([0-9a-z]+)/$', views.task_info),
]
