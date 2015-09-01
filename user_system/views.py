#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'defaultstr'

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from django.template import RequestContext

from .forms import *
from .models import User, ResetPasswordRequest, TimestampGenerator
from .utils import *

import datetime


def login(request):
    form = LoginForm()
    error_message = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if not request.session.test_cookie_worked():
                error_message = u'Cookie错误，请再试一次'
            else:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                error_code, user = authenticate(username, password)
                user.login_num += 1
                user.save()
                if error_code == 0:
                    store_in_session(request, user)
                    return redirect_to_prev_page(request, '/home/')
                elif error_code == 1:
                    error_message = u'用户不存在，请检查用户名是否正确'
                elif error_code == 2:
                    error_message = u'密码错误，请重新输入密码'
        else:
            error_message = u'表单输入错误'

    request.session.set_test_cookie()
    return render_to_response(
        'login.html',
        {
            'form': form,
            'error_message': error_message,
        },
        RequestContext(request)
    )


def signup(request):
    form = SignupForm()
    error_message = None

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User()
            user.username = form.cleaned_data['username']
            user.password = form.cleaned_data['password']
            user.email = form.cleaned_data['email']
            user.sex = form.cleaned_data['sex']
            user.class_no = form.cleaned_data['class_no']

            user.signup_time = datetime.datetime.now()
            user.last_login = datetime.datetime.now()
            user.login_num = 0
            user.save()
            return HttpResponseRedirect('/user/login/')
        else:
            error_message = form.errors

    return render_to_response(
        'signup.html',
        {'form': form,
         'error_message': error_message,
         },
        RequestContext(request)
    )


def logout(request):
    if 'username' in request.session:
        del request.session['username']
    if 'prev_page' in request.session:
        del request.session['prev_page']
    return HttpResponseRedirect('/user/login/')


@require_login
def info(user, request):
    return render_to_response(
        'info.html',
        {
            'cur_user': user
        },
        RequestContext(request),
    )


@require_login
def edit_info(user, request):
    form = EditInfoForm(
        {
            'email': user.email,
            'sex': user.sex,
            'class_no': user.class_no,
        })
    error_message = None

    if request.method == 'POST':
        form = EditInfoForm(request.POST)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            user.sex = form.cleaned_data['sex']
            user.class_no = form.cleaned_data['class_no']
            user.save()
            return HttpResponseRedirect('/user/info/')
        else:
            error_message = form.errors

    return render_to_response(
        'edit_info.html',
        {
            'cur_user': user,
            'form': form,
            'error_message': error_message,
        },
        RequestContext(request),
    )


@require_login
def edit_password(user, request):
    form = EditPasswordForm()
    error_message = None

    if request.method == 'POST':
        form = EditPasswordForm(request.POST)
        if form.is_valid():
            if user.password == form.cleaned_data['cur_password']:
                user.password = form.cleaned_data['new_password']
                user.save()
                return HttpResponseRedirect('/user/info/')
            else:
                error_message = '原密码错误'
        else:
            error_message = form.errors

    return render_to_response(
        'edit_password.html',
        {
            'cur_user': user,
            'form': form,
            'error_message': error_message,
        },
        RequestContext(request),
    )


def forget_password(request):
    form = ForgetPasswordForm()
    error_message = None

    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects(email=form.cleaned_data['email'])
            if user is None or len(user) == 0:
                error_message = u'Email地址不存在'
            else:
                user = user[0]
                reset_request = ResetPasswordRequest.objects.create(
                    user=user
                )
                reset_request.save()
                send_reset_password_email(request, reset_request)
                return HttpResponseRedirect('/user/login/')
        else:
            error_message = form.errors

    return render_to_response(
        'forget_password.html',
        {
            'form': form,
            'error_message': error_message,
        },
        RequestContext(request),
    )


def reset_password(request, token_str):
    form = ResetPasswordForm()
    token = None
    error_message = None

    try:
        token = ResetPasswordRequest.objects.get(token=token_str)
        print TimestampGenerator(0)()
        print token.expire
        if TimestampGenerator(0)() > token.expire:
            error_message = u'Token已失效，请重新找回密码'
    except DoesNotExist:
        error_message = u'链接地址错误，请重新找回密码'

    if error_message is not None:
        return render_to_response(
            'reset_password.html',
            {
                'form': None,
                'error_message': error_message
            },
            RequestContext(request),
        )

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = token.user
            user.password = form.cleaned_data['new_password']
            user.save()
            return HttpResponseRedirect('/user/login/')
        else:
            error_message = form.errors

    return render_to_response(
        'reset_password.html',
        {
            'form': form,
            'error_message': error_message,
        },
        RequestContext(request),
    )

