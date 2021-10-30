#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : tag_base
@Author     : LeeCQ
@Date-Time  : 2021/8/30 20:13
"""
from munch import Munch, unmunchify, munchify

from common import set_conf
from config import msal_info
from ext import DiskTagException
from utest.ut_common import get_conf

TAG_NEW = 1  # 新的, 待安装 Tag
TAG_EXIST = 0  # 可用的, 现有的 Tag
TAG_ERROR = -1  # 错误的 Tag
legal_character = 'QqWwEeRrTtYyUuIiOoPpAaSsDdFfGgHhJjKkLlZzXxCcVvBbNnMm-_1234567890'


class TagBase:
    """"""

    def __init__(self, disk_tag, checked=False, conf_file=None):
        self.conf_file = conf_file
        self.disk_tag = disk_tag
        self.tag_flag = None  # TAG的标记, 新的, 可用的, 错误的

        self.disk_conf_key = 'disks.{disk_tag}'.format(disk_tag=disk_tag)  # TODO 尝试将此写入配置文件
        self.disk_conf = Munch()  # disk_tag 的反序列化

        self.get_disk_conf()
        self.tag_flag, self.tag_error_desc = (TAG_EXIST, '') if checked else self.check_tag()
        self.checked = True

    def raise_tag_error(self):
        if self.tag_flag == TAG_ERROR:
            raise DiskTagException(self.tag_error_desc)

    def check_tag(self) -> (int, str):
        """检查输入的tag的合法性
            不能和已有的tag重复;
            不能有是关键字;
            不能包含特殊字符;

            只检查不修改;
        """
        disk_tag = self.disk_tag
        conf = get_conf('*', file=self.conf_file)
        try:
            if conf['disks'][disk_tag]:
                return TAG_EXIST, '已存在'
        except:
            pass

        if not isinstance(disk_tag, str):
            self.disk_tag = TAG_ERROR
            return TAG_ERROR, 'disk_tag 必须是字符串'

        if not (3 <= len(disk_tag) <= 15):
            return TAG_ERROR, '长度应该在 3-15之间'

        try:  # ascii 字符检测
            disk_tag.encode(encoding='ascii')
        except UnicodeError:
            return TAG_ERROR, '必须只包含ascii字符'

        for _char in disk_tag:
            if _char not in legal_character:
                return TAG_ERROR, f'{disk_tag} 包含不合法字符 "{_char}", 仅支持数字/字母/中划线/下划线 '

        if disk_tag[0] in '1234567890_-' or disk_tag[-1] in '1234567890_-':
            return TAG_ERROR, '不能以数字,中划线,下划线开头或结尾'

        if disk_tag in conf.keys():
            return TAG_ERROR, f'{disk_tag=} 名称不合法, 与已有关键字冲突.'

        return TAG_NEW, '全新的'

    def create_tag(self):
        if self.tag_flag == TAG_NEW:
            set_conf(f'disks.{self.disk_tag}', {})

    def save_disk_conf(self):
        set_conf(self.disk_conf_key, unmunchify(self.disk_conf), file=self.conf_file, )

    def get_disk_conf(self):
        self.disk_conf = munchify(get_conf(self.disk_conf_key, file=self.conf_file) or msal_info)

    refresh_conf = get_disk_conf
