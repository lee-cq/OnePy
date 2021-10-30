#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : ext
@Author     : LeeCQ
@Date-Time  : 2021/8/4 19:04
"""


class OneException(Exception):
    """Base Exception """


class DiskTagException(OneException):
    """Tag名称不合法"""


class NotInstallError(OneException):
    """未安装"""


class DiskErrorBase(OneException):
    """ Disk对象Error"""


class ItemErrorBase(OneException):
    """Item对象基础错误"""
