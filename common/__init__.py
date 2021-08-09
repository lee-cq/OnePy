#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : __init__.py
@Author     : LeeCQ
@Date-Time  : 2021/8/5 19:59
"""
import sys
from pathlib import Path as __Path

__BASE__ = __Path(__file__).parent.absolute()
sys.path.append(str(__BASE__))

from config_operation import set_conf, get_conf
# from zip_pathlib import PathCompress

SUCCESS = 0
FAIL = -1
