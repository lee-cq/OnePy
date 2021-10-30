#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : ut_admin
@Author     : LeeCQ
@Date-Time  : 2021/8/7 2:13

"""
import unittest

from utest.ut_common import set_conf, get_conf, conf_json
from admin.ms_token import *


class AdminTag(unittest.TestCase):
    """验证TAG情况"""

    def setUp(self) -> None:
        conf_json.write_text(
            '{"disks": {"disk1": {"Client_ID": "aa", "Client_Sea": "bb", "token_cache": "cc"}},"lists": ["a", "b"]}'
        )

    def tag_case(self, tag_list, expect, msg):
        """"""
        for tag_name in tag_list:
            with self.subTest(msg=msg, tag=tag_name, expect=expect):
                _t = TagBase(tag_name, conf_file=conf_json)
                self.assertEqual(_t.tag_flag, expect)

    def test_tag_new(self):
        """新tag检测"""
        _t = TagBase('new_tag_name', conf_file=conf_json)
        self.assertEqual(_t.tag_flag, TAG_NEW)

    def test_tag_exist(self):
        """已存在tag检测"""
        _t = TagBase('disk1', conf_file=conf_json)
        self.assertEqual(_t.tag_flag, TAG_EXIST)

    def test_test_error(self):
        """错误tag检测"""
        _error_case = [
            'a+1', '[0]', 'asl*5', 'b/sd', '1234567890', '-1234asd', 'asd123-'
        ]
        self.tag_case(_error_case, TAG_ERROR, '错误tag检测')


class AdminMSToken(unittest.TestCase):
    """验证MSToken"""
