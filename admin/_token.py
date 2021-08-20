#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : token
@Author     : LeeCQ
@Date-Time  : 2021/8/3 23:50

该模块实现对msal Token 获取,更新, 实现全封装

"""
import msal

from common import SUCCESS, FAIL
from common import get_conf, set_conf
from common.zip_pathlib import PathCompress
from config import PATH_TOKEN_CACHE

TAG_NEW = 0  # 新的, 待安装 Tag
TAG_USABLE = 1  # 可用的, 现有的 Tag
TAG_EXIST = 2  # 已经存在的 Tag
TAG_ERROR = -1  # 错误的 Tag


class TokenBase:
    """"""

    def __init__(self, disk_tag):
        self.disk_tag = disk_tag
        self.tag_flag = None  # TAG的标记, 新的, 可用的, 错误的
        self.check_tag()

    def check_tag(self, disk_tag=None):
        """检查输入的tag的合法性
            不能和已有的tag重复;
            不能有是关键字;
            不能包含特殊字符;

            只检查不修改;
        """
        disk_tag = disk_tag or self.disk_tag
        conf = get_conf('*')
        import re

        if not re.search(r'[\W \t<>,.:";\'=+/\\*!@#$%^&()]', disk_tag):
            self.tag_flag = TAG_ERROR
            raise ValueError(f'{disk_tag=} 名称不合法, 仅支持数字/字母/汉字/中划线/下划线 ')

        if disk_tag in conf.keys() or disk_tag in conf.get('disks'):
            self.tag_flag = TAG_ERROR
            raise ValueError(f'{disk_tag=} 名称不合法, 与已有关键字冲突 ')

        try:
            self.tag_flag = TAG_USABLE if disk_tag in conf.get('disks').keys() else TAG_NEW
        except KeyError:
            self.tag_flag = TAG_NEW

        self.disk_tag = disk_tag

    def create_tag(self):
        if self.tag_flag == TAG_NEW:
            set_conf(f'disks.{self.disk_tag}', {})


class MSALToken(TokenBase):
    """处理 MSAL Token Cache 的集成类 """

    def __init__(self, disk_tag):
        super().__init__(disk_tag)

        self.disk_token = PathCompress(PATH_TOKEN_CACHE).joinpath(disk_tag)
        self.msal_conf = get_conf(f'disks.{disk_tag}')

        self.token_cache = msal.SerializableTokenCache()

    def save_cache(self, ):
        if self.token_cache.has_state_changed:
            self.disk_token.write_text(self.token_cache.serialize())
            set_conf(f'disks.{self.disk_tag}.token', self.token_cache.serialize())
            return SUCCESS
        else:
            return FAIL

    def load_cache(self):
        """加载缓存"""
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
        if accounts:
            result = cca.acquire_token_silent(scope, account=accounts[0])  # 成功后缓存对象会被更新, 通过msal-App
            return result
        else:
            return FAIL

    def set_client_id_secret(self, client_id, client_secret):
        if self.tag_flag != TAG_ERROR:
            set_conf(f'disks.{self.disk_tag}.CLIENT_ID', client_id)
            set_conf(f'disks.{self.disk_tag}.CLIENT_SECRET', client_secret)
            return SUCCESS
        else:
            return FAIL


if __name__ == '__main__':
    pass
