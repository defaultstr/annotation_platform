#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from mongoengine import *
from .forms import *
from hashlib import sha512
from uuid import uuid4
import time

user_group_list = (
    ('admin', u'管理员'),
    ('normal_user', u'普通用户'),
)

class TimestampGenerator(object):

    def __init__(self, seconds=0):
        self.seconds = seconds

    def __call__(self):
        return int(time.time()) + self.seconds


class KeyGenerator(object):

    def __init__(self, length):
        self.length = length

    def __call__(self):
        key = sha512(uuid4().hex).hexdigest()[0:self.length]
        return key


class User(Document):
    username = StringField(unique=True, required=True)
    password = StringField(required=True)
    email = EmailField(required=True)
    sex = StringField(choices=sex_choices)
    class_no = StringField()

    user_groups = ListField(StringField(choices=user_group_list), default=['normal_user'])

    signup_time = DateTimeField()
    last_login = DateTimeField()
    login_num = IntField()
    credit = IntField()


class ResetPasswordRequest(Document):
    user = ReferenceField(User)
    token = StringField(default=KeyGenerator(12))
    expire = IntField(default=TimestampGenerator(60*60*30))


