#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : item
@Author     : LeeCQ
@Date-Time  : 2021/8/30 20:12
"""
from common.tag_base import TagBase
from onedrive import DriverItem


class Item():

    @classmethod
    def __new__(cls, disk_tag, *args, **kwargs):
        _conf = TagBase(disk_tag=disk_tag, conf_file=kwargs.get('conf_file', None)).disk_conf
        if _conf.DRIVE_TYPE == 'onedrive':
            return DriverItem(disk_tag, *args, **kwargs)


Item('test')
