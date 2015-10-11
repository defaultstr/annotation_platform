#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = [
    url(r'^home/$', views.list_tasks),
    url(r'^next_task/([0-9a-z]+)/$', views.get_next_task_unit),
    url(r'^anno/([0-9a-z]+)/([0-9a-z]+)/', views.annotate),
]
