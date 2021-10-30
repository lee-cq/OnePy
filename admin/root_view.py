#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : root_view
@Author     : LeeCQ
@Date-Time  : 2021/8/24 23:29
"""
from flask import Blueprint

from .ms_token import get_token as _get_token

root = Blueprint('root', __name__, url_prefix='/')


@root.route('/getAToken')
def get_token():
    return _get_token()
