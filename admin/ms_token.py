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

from common import SUCCESS, FAIL
from common.tag_base import TagBase, TAG_ERROR, TAG_EXIST
from common.zip_pathlib import PathCompress
from config import PATH_TOKEN_CACHE


# onedrive_token = Blueprint('onedrive', 'onedrive', url_prefix='/onedrive')


class MSALToken(TagBase):
    """处理 MSAL Token Cache 的集成类 """

    def __init__(self, disk_tag, checked=False, conf_file=None):
        super().__init__(disk_tag, checked, conf_file)

        self.disk_token = PathCompress(PATH_TOKEN_CACHE).joinpath(disk_tag)  # 磁盘中的序列化的缓存的位置

        self.token_cache = msal.SerializableTokenCache()
        self.refresh_conf()
        self.load_cache()
        self.raise_tag_error()

    def save_cache(self):
        """保存缓存信息"""
        if self.token_cache.has_state_changed:
            __serialize_token = self.token_cache.serialize()
            self.disk_token.write_text(__serialize_token)  # 单文件持久化
            self.disk_conf.token = __serialize_token  # 保存在conf中
            self.save_disk_conf()
            return SUCCESS
        else:
            return FAIL

    def load_cache(self):
        """加载缓存"""
        if _t := self.disk_conf.get('token', None):  # 从配置中加载
            self.token_cache.deserialize(_t)
        elif self.disk_token.exists():  # 从缓存Token文件中加载
            self.token_cache.deserialize(self.disk_token.decompress())

    def build_msal_app(self):
        # 为服务端获取令牌
        # print('构造令牌APP')
        return msal.ConfidentialClientApplication(
            self.disk_conf['CLIENT_ID'], authority=self.disk_conf['AUTHORITY'],
            client_credential=self.disk_conf.CLIENT_SECRET, token_cache=self.token_cache)

    def _build_auth_code_flow(self, scopes=None):
        """工具函数, 获取构建认证流信息"""
        # print('构造认证流信息')
        return self.build_msal_app().initiate_auth_code_flow(
            scopes or self.disk_conf.SCOPES,
            redirect_uri=url_for("root.get_token", _external=True,
                                 # disk_tag=self.disk_tag
                                 )
        )

    def build_auth_code_flow_uri(self, scopes=None):
        """将获取到的认证流信息保存并返回URI"""
        self.disk_conf.AUTH_FLOW = self._build_auth_code_flow(scopes)
        self.save_disk_conf()
        return self.disk_conf.AUTH_FLOW.get('auth_uri')

    def get_token_from_cache(self, force_refresh=False):
        cca = self.build_msal_app()
        accounts = cca.get_accounts()
        if accounts:
            result = cca.acquire_token_silent(self.disk_conf.SCOPES,
                                              account=accounts[0],
                                              force_refresh=force_refresh)  # 成功后缓存对象会被更新, 通过msal-App
            self.save_cache()
            return result
        else:
            return FAIL

    def set_client_id_secret(self, client_id, client_secret, description):
        if self.tag_flag != TAG_ERROR:
            self.disk_conf.CLIENT_ID = client_id or os.environ.get('CLIENT_ID')
            self.disk_conf.CLIENT_SECRET = client_secret or os.environ.get('CLIENT_SECRET')
            self.disk_conf.description = description
            self.save_disk_conf()
            return SUCCESS
        else:
            return FAIL


def get_token():
    """被引用的视图函数"""
    try:
        _token = MSALToken(current_app.config.pop('adding_disk_tag'))
        if _token.tag_flag != TAG_EXIST:
            return 'TAG Name 不存在或错误'
        result = _token.build_msal_app().acquire_token_by_auth_code_flow(
            _token.disk_conf.get('AUTH_FLOW', {}),
            request.args
        )
        print(result)
        if "error" in result:  # 返回错误页
            return render_template("error_redirect.html",
                                   title='OneDrive账户认证失败, 请重试',
                                   body=result,
                                   url=url_for('admin.add_disk_index')
                                   )

        _token.disk_conf.MS_USERNAME = result.get("id_token_claims").get("preferred_username")

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
        request.form.get('client_secret', ),
        request.form.get('description', '')
    )
    r_url = redirect(_token.build_auth_code_flow_uri())
    current_app.config.update(adding_disk_tag=request.form['tag_name'])
    return r_url


if __name__ == '__main__':
    pass
