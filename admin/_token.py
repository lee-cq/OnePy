#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : token
@Author     : LeeCQ
@Date-Time  : 2021/8/3 23:50

该模块实现对msal Token 获取,更新, 实现全封装

"""
import os

import msal
from flask import url_for, redirect, request, render_template, current_app
from munch import munchify, unmunchify

from common import SUCCESS, FAIL
from common import get_conf, set_conf
from common.zip_pathlib import PathCompress
from config import PATH_TOKEN_CACHE, msal_info

TAG_NEW = 0  # 新的, 待安装 Tag
TAG_EXIST = 1  # 可用的, 现有的 Tag
TAG_ERROR = -1  # 错误的 Tag


# onedrive_token = Blueprint('onedrive', 'onedrive', url_prefix='/onedrive')


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

        if not isinstance(disk_tag, str):
            self.disk_tag = TAG_ERROR
            raise TypeError(f'类型错误应该是 Str 但是得到 {type(disk_tag)}')

        import re

        if re.search(r'[\W \t<>,.:";\'=+/\\*!@#$%^&()]', disk_tag):
            self.tag_flag = TAG_ERROR
            raise ValueError(f'{disk_tag=} 名称不合法, 仅支持数字/字母/汉字/中划线/下划线 ')

        if disk_tag in conf.keys():
            self.tag_flag = TAG_ERROR
            raise ValueError(f'{disk_tag=} 名称不合法, 与已有关键字冲突 ')

        try:
            self.tag_flag = TAG_EXIST if disk_tag in conf.get('disks').keys() else TAG_NEW
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

        self.msal_conf_key = f'disks.{disk_tag}'

        self.disk_token = PathCompress(PATH_TOKEN_CACHE).joinpath(disk_tag)  # 磁盘中的序列化的缓存
        self.msal_conf = munchify(get_conf(self.msal_conf_key) or msal_info)  # disk_tag 的序列化

        self.token_cache = msal.SerializableTokenCache()
        self.load_cache()

    def save_conf(self):
        set_conf(self.msal_conf_key, unmunchify(self.msal_conf))

    def refresh_conf(self):
        self.msal_conf = munchify(get_conf(self.msal_conf_key))

    def save_cache(self):
        """保存缓存信息"""
        if self.token_cache.has_state_changed:
            self.disk_token.write_text(self.token_cache.serialize())  # 单文件持久化
            self.msal_conf.token = self.token_cache.serialize()  # 保存在conf中
            self.save_conf()
            return SUCCESS
        else:
            return FAIL

    def load_cache(self):
        """加载缓存"""
        if _t := self.msal_conf.get('token', None):  # 从配置中加载
            self.token_cache.deserialize(_t)
        elif self.disk_token.exists():  # 从缓存Token文件中加载
            self.token_cache.deserialize(self.disk_token.decompress())

    def build_msal_app(self):
        # 为服务端获取令牌
        print('构造令牌APP')
        return msal.ConfidentialClientApplication(
            self.msal_conf['CLIENT_ID'], authority=self.msal_conf['AUTHORITY'],
            client_credential=self.msal_conf.CLIENT_SECRET, token_cache=self.token_cache)

    def _build_auth_code_flow(self, scopes=None):
        """工具函数, 获取构建认证流信息"""
        print('构造认证流信息')
        return self.build_msal_app().initiate_auth_code_flow(
            scopes or self.msal_conf.SCOPES,
            redirect_uri=url_for("root.get_token", _external=True,
                                 # disk_tag=self.disk_tag
                                 )
        )

    def build_auth_code_flow_uri(self, scopes=None):
        """将获取到的认证流信息保存并返回URI"""
        self.msal_conf.AUTH_FLOW = self._build_auth_code_flow(scopes)
        self.save_conf()
        return self.msal_conf.AUTH_FLOW.get('auth_uri')

    def get_token_from_cache(self, scope=None):
        cca = self.build_msal_app()
        accounts = cca.get_accounts()
        if accounts:
            result = cca.acquire_token_silent(scope, account=accounts[0])  # 成功后缓存对象会被更新, 通过msal-App
            return result
        else:
            return FAIL

    def set_client_id_secret(self, client_id, client_secret):
        if self.tag_flag != TAG_ERROR:
            self.msal_conf.CLIENT_ID = client_id or os.environ.get('CLIENT_ID')
            self.msal_conf.CLIENT_SECRET = client_secret or os.environ.get('CLIENT_SECRET')
            set_conf(f'disks.{self.disk_tag}', self.msal_conf)
            return SUCCESS
        else:
            return FAIL


def get_token():
    try:
        _token = MSALToken(current_app.config.pop('adding_disk_tag'))
        if _token.tag_flag != TAG_EXIST:
            return 'TAG Name yichang'
        result = _token.build_msal_app().acquire_token_by_auth_code_flow(
            _token.msal_conf.get('AUTH_FLOW', {}),
            request.args
        )
        print(result)
        if "error" in result:  # 返回错误页
            return render_template("error_redirect.html",
                                   title='OneDrive账户认证失败, 请重试',
                                   body=result,
                                   url=url_for('admin.add_disk_index')
                                   )

        _token.msal_conf.MS_USERNAME = result.get("id_token_claims").get("preferred_username")

        if _token.save_cache() == SUCCESS:
            return render_template("error_redirect.html",
                                   title='OneDrive账户认证成功',
                                   body='登录成功',
                                   url=url_for('admin.index')
                                   )

    except ValueError as _e:  # Usually caused by CSRF
        raise _e  # Simply ignore them
    return '登录异常'


def view():
    from flask import request

    _token = MSALToken(request.form['tag_name'])
    _token.set_client_id_secret(
        request.form.get('client_id', ),
        request.form.get('client_secret', )
    )
    r_url = redirect(_token.build_auth_code_flow_uri())
    current_app.config.update(adding_disk_tag=request.form['tag_name'])
    return r_url


if __name__ == '__main__':
    pass
