#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : view
@Author     : LeeCQ
@Date-Time  : 2021/8/7 0:49
"""
import json
from dataclasses import dataclass

from flask import Blueprint
from flask import request, render_template
from flask_login import LoginManager, login_required, login_user, UserMixin

from common.config_operation import get_conf
from config import BASE_PATH_CODE

admin = Blueprint('admin', __name__, url_prefix='/admin',
                  static_folder=BASE_PATH_CODE.joinpath('static').__str__()
                  )

login_manager = LoginManager()
login_manager.login_view = "admin.login"


@dataclass
class User(UserMixin):
    """"""
    id: int
    password: str


user = User(get_conf('username'), get_conf('password'))


@login_manager.user_loader
def load_user(user_id):
    return user if get_conf('username') == user_id else None


@admin.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == "GET":
        return render_template('login.html')

    err_msg = {"result": "NO"}
    param = json.loads(request.data.decode("utf-8"))
    username = param.get("username", "")
    password = param.get("password", "")
    print(username, get_conf('username'), password, get_conf('password'))
    if username == get_conf('username') and password == get_conf('password'):
        login_user(user)
        _next = request.args.get('next')
        print(_next)
        return {"result": "OK", 'next': _next[:-1] if _next.endswith('/') else _next}
    return err_msg | {'msg': '用户名或密码错误'}


@admin.route('/')
@login_required
def index():
    return 'Hello, Admin'


@admin.route('/setClient', methods=['POST'])
@login_required
def set_client():
    pass


@admin.route('/add-disk')
@login_required
def add_disk_index():
    return render_template('add_disk.html')


@admin.route('/add-disk/<name>', methods=['POST'])
@login_required
def add_disk(name):
    """

    @param name: 磁盘类型
    """
    if name == 'onedrive':
        from ._token import view
        return view()
