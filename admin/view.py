#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : view
@Author     : LeeCQ
@Date-Time  : 2021/8/7 0:49
"""
from flask import Blueprint

bp = Blueprint('', '')


@bp.route('/setClient', methods=['POST'])
def set_client():
    pass


@bp.route('/getToken')
def get_token():
    pass
