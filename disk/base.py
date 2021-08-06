#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : base
@Author     : LeeCQ
@Date-Time  : 2021/8/4 20:41

为了解耦, disk对象和item对象
"""
import abc


class DiskBase(abc.ABC):
    """磁盘基类, 适用于可拓展的disk对象.

    Disk 的操作始终着眼于一个Item对象,
    """

    @abc.abstractmethod
    def api_client(self, uri, *args, **kwargs):
        """API 请求入口"""

    @abc.abstractmethod
    def upload(self):
        pass
