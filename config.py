#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : config
@Author     : LeeCQ
@Date-Time  : 2021/8/3 23:41
"""
from json import dumps as _dumps
from pathlib import Path as _Path

# 所有的路径务必使用Path封装一次
# 代码的基础路径
BASE_PATH_CODE = _Path(__file__).absolute().parent
# 项目资源的基础路径
BASE_PATH_FS = _Path(__file__).absolute().parent

# 缓存Token的路径
PATH_TOKEN_CACHE = BASE_PATH_FS.joinpath('.cache_token')
PATH_TOKEN_CACHE.mkdir(mode=0o700, parents=True, exist_ok=True)

# 单元测试资源文件路径
PATH_UT_RESOURCES = BASE_PATH_CODE / 'utest' / 'resources'

# 环境变量存放地址
FILE_ENV_MSAL_CLIENT = BASE_PATH_FS / '.env_msal'

# 项目配置的基础路径
FILE_CONF_JSON = BASE_PATH_FS / 'conf.json'


class _MASLToken:
    """默认的配置"""
    AUTHORITY = "https://login.microsoftonline.com/organizations"
    REDIRECT_PATH = "/getAToken"
    SCOPE = ["User.ReadBasic.All", "Files.ReadWrite.All", "Sites.ReadWrite.All"]
    SESSION_TYPE = "filesystem"
    CLIENT_ID = ''
    CLIENT_SECRET = ''

    @classmethod
    def dict(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}

    @classmethod
    def __str__(cls):
        return _dumps(cls.dict())
