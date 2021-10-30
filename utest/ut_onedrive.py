#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : ut_onedrive
@Author     : LeeCQ
@Date-Time  : 2021/8/4 23:33
"""

import unittest

from config import PATH_UT_RESOURCES
from disk.onedrive import MSClient

ONEDRIVE_CONF = PATH_UT_RESOURCES / 'onedrive_conf.json'


class UTMSToken(unittest.TestCase):
    """"""

    _ms_token = MSClient('test', conf_file=ONEDRIVE_CONF)

    def test_0_token_from_cache(self):
        """"""
        # print(self._ms_token.token_cache.key_makers['AccessToken']())
        self._ms_token.get_token_from_cache()

    def test_1_access_token(self):
        self._ms_token.access_token

