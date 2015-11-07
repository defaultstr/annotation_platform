#!/user/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from django import forms
from task_manager.settings import tag2controller

tag_choices = tuple([(x, x) for x in tag2controller])


class NewTaskForm(forms.Form):
    task_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control login-field',
                'placeholder': u'任务名称',
            }
        )
    )
    task_description = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control login-field',
                'placeholder': u'任务描述',
            }
        )
    )
    task_tag = forms.ChoiceField(
        required=True,
        choices=tag_choices,
        widget=forms.Select(
            attrs={
                'class': 'select2-container form-control select select-primary'
            }
        )
    )

