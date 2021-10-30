#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : common
@Author     : LeeCQ
@Date-Time  : 2021/8/3 23:35
"""
import json

from common.zip_pathlib import PathCompress
from config import FILE_CONF_JSON


def get_conf(key: str, file=FILE_CONF_JSON) -> [dict, str, int, float, bool, None]:
    """从配置文件中拿取一个配置"""
    file = PathCompress(file if file else FILE_CONF_JSON)
    conf_dict = json.loads(file.read_conf())
    if key == '*':  # 允许查询全部的内容
        return conf_dict

    _m_key = key.split('.')
    _value = conf_dict

    for k in _m_key:
        _value = _value.get(k, None)
        if _value is None:
            return _value
    return _value


def json_default_replace(_in):
    """将类型转化为Json识别的对象"""
    if isinstance(_in, set):
        return list(_in)
    raise TypeError(f'JSON 序列号失败,如果你认为该值({_in})是可以被写入JSON的, 改写 {__file__} 的 json_default_replace 函数;'
                    f'\n将其转换为 dict, str, int, float, bool, None 的一种. ')


def set_conf(key, value, rewrite=False, file=FILE_CONF_JSON):
    """设置一个键到conf.json"""

    def _set_conf(_key: [str, list], _value, _dict):
        _m_key = _key.split('.') if isinstance(_key, str) else _key
        if _m_key.__len__() != 0:
            _k = _m_key.pop(0)
            _dict[_k] = _set_conf(_m_key, _value, _dict.get(_k, {}))
            return _dict
        else:
            return _value

    file = PathCompress(file if file else FILE_CONF_JSON)
    if key == '*':
        return file.write_conf(json.dumps(value, ensure_ascii=False, default=json_default_replace, indent=2))

    conf_dict = json.loads(file.read_conf())
    new_conf = _set_conf(key, value, conf_dict)
    return file.write_conf(
        json.dumps(new_conf, ensure_ascii=False, default=json_default_replace, indent=2)
    )


if __name__ == '__main__':
    print(get_conf('disks.disk1'))
    set_conf('disks.disk1.Client_ID_', 'aa', )
