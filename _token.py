#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : token
@Author     : LeeCQ
@Date-Time  : 2021/8/3 23:50

该模块实现对msal Token 获取,更新, 实现全封装

"""

import msal
from flask import Blueprint

from common import SUCCESS
from common import get_conf, set_conf
from common.zip_str import PathCompress
from config import PATH_TOKEN_CACHE

bp_token = Blueprint('token', 'token')


class MSALToken:
    """处理 MSAL Token Cache 的集成类 """

    def __init__(self, disk_tag):
        self.disk_tag = disk_tag
        self.disk_token = PathCompress(PATH_TOKEN_CACHE).joinpath(disk_tag)
        self.msal_conf = get_conf(f'disks.{disk_tag}')

        self.token_cache = msal.SerializableTokenCache()

    def save_cache(self, ):
        if self.token_cache.has_state_changed:
            self.disk_token.write_text(self.token_cache.serialize())
            return SUCCESS

    def load_cache(self):
        if self.disk_token.exists():
            self.token_cache.deserialize(self.disk_token.decompress())

    def _build_msal_app(self):
        # 为服务端获取令牌
        return msal.ConfidentialClientApplication(
            self.msal_conf['CLIENT_ID'], authority=self.msal_conf['AUTHORITY'],
            client_credential=self.msal_conf.CLIENT_SECRET, token_cache=self.token_cache)

    def get_token_from_cache(self, scope=None):
        cca = self._build_msal_app()
        accounts = cca.get_accounts()
        if accounts:  # So all account(s) belong to the current signed-in user
            result = cca.acquire_token_silent(scope, account=accounts[0])  # 成功后缓存对象会被更新, 通过msal-App
            return result


@bp_token.route('/setClient', methods=['POST'])
def set_client():
    pass


@bp_token.route('/getToken')
def get_token():
    pass
