#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : install
@Author     : LeeCQ
@Date-Time  : 2021/8/8 18:54

检查运行环境;  v
设置全局SESSION秘钥;  v
初始化config.json v
添加管理员密码  v


"""
import os
import sys
from pathlib import Path
from base64 import b64encode

from config import BASE_PATH_CODE, conf_json
from common.config_operation import set_conf, get_conf


def is_venv():
    """当前启动器是否是虚拟隔离环境"""
    return True if Path(sys.prefix).parent.absolute() == BASE_PATH_CODE.joinpath('venv').absolute() else False


def install_requirements():
    """ 安装依赖 """
    os.system(f'pip install -r {BASE_PATH_CODE.joinpath("requirements.txt")}')


def install_config_json():
    set_conf('*', conf_json)


def install_SECRET_KEY(force=False):
    """安装 SECRET_KEY, 同时作为已经安装的标志. """
    if not get_conf('SECRET_KEY') or force:
        set_conf(f'SECRET_KEY', b64encode(os.urandom(16)).decode())
    else:
        raise FileExistsError(f'重复安装异常, 重置请删除 .installed 文件或使用 force=True')


def install_admin_user():
    set_conf('username', 'admin')
    set_conf('password', input('输入管理员密码: '))


def main():
    is_venv()
    install_requirements()
    install_config_json()
    install_admin_user()
    install_SECRET_KEY()


if __name__ == '__main__':
    main()
