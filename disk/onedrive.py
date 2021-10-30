#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : onedrive.py
@Author     : LeeCQ
@Date-Time  : 2021/8/28 15:43
"""

import time
from pathlib import Path

from requests import Session

from admin.ms_token import MSALToken


class MSClient(MSALToken, Session):

    def __init__(self, disk_tag, conf_file=None):
        super().__init__(disk_tag, conf_file)

        self._access_token = None

    def get_token_from_cache(self, force_refresh=False):
        """重写token缓存, 添加内存缓存"""
        _token = super(MSClient, self).get_token_from_cache(force_refresh)
        _token['expires_at'] = _token['expires_in'] + int(time.time())
        self._access_token = _token
        return _token

    @property
    def access_token(self) -> str:
        """取得一个Access Token

        @return: Access Token
        """
        try:
            if self._access_token['expires_at'] >= time.time() - 1000:  # 正常
                return self._access_token['access_token']
            else:  # 超时
                return self.get_token_from_cache(force_refresh=True)['access_token']

        except (KeyError, TypeError):  # 没有
            return self.get_token_from_cache()['access_token']

    def request(self, url, method, is_auth: bool = True, **kwargs):
        __headers = {'Authorization': 'Bearer ' + self.access_token} if is_auth else {}
        __headers.update(kwargs.pop('headers') if 'headers' in kwargs else {})

        return self.request(method=method, url=url, headers=__headers, **kwargs)


class DriverItem(MSClient):
    """"""

    def __init__(self, disk_tag, path='/', conf_path=None):
        """初始化"""
        super().__init__(disk_tag, conf_file=conf_path)
        self.path = path
