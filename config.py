#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : config
@Author     : LeeCQ
@Date-Time  : 2021/8/3 23:41
"""
from json import dumps as _dumps
from common.zip_str import PathCompress as _Path

# from dotenv import get_key

BASE_PATH_CODE = _Path(__file__).absolute().parent
BASE_PATH_FS = _Path(__file__).absolute().parent

PATH_TOKEN_CACHE = BASE_PATH_FS.joinpath('.cache_token')
PATH_TOKEN_CACHE.mkdir(mode=0o700, parents=True, exist_ok=True)
PATH_UT_RESOURCES = BASE_PATH_FS / 'utest' / 'resources'

FILE_ENV_MSAL_CLIENT = BASE_PATH_FS / '.env_msal'
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
