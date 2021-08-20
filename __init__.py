#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : __init__.py
@Author     : LeeCQ
@Date-Time  : 2021/8/8 19:11
"""

import flask
from dotenv import load_dotenv

from common import get_conf
from config import BASE_PATH_CODE
from ext import NotInstallError

load_dotenv('.env', override=True)
SECRET_KEY = get_conf('SECRET_KEY')


def create_app():
    app = flask.Flask(__name__)

    if not SECRET_KEY:
        raise NotInstallError(f'未正确安装Session秘钥 .')

    app.config['SECRET_KEY'] = SECRET_KEY

    from admin.view import login_manager, admin
    login_manager.init_app(app)
    app.register_blueprint(admin)

    return app


if __name__ == '__main__':
    a = create_app()
    a.run(host='localhost', port=8081)
