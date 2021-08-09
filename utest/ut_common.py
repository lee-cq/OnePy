#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : ut_common
@Author     : LeeCQ
@Date-Time  : 2021/8/4 23:33
"""
import unittest

from zlib import decompress, compress

from config import PATH_UT_RESOURCES
from common import get_conf as _get_conf, set_conf as _set_conf
from common.zip_pathlib import PathCompress

conf_json = PATH_UT_RESOURCES / 'conf.json'


def set_conf(k, v, file=conf_json):
    """"""
    return _set_conf(k, v, file=file)


def get_conf(k, file=conf_json):
    """"""
    return _get_conf(k, file=file)


class CommonConf(unittest.TestCase):
    conf_json = PATH_UT_RESOURCES / 'conf.json'

    def setUp(self) -> None:
        self.conf_json.write_text(
            '{"disks": {"disk1": {"Client_ID": "aa", "Client_Sea": "bb", "token_cache": "cc"}},"lists": ["a", "b"]}')

    def test_11_get_str(self):
        """获取已经存在的键"""
        a = get_conf('disks.disk1.Client_ID', file=self.conf_json)
        self.assertEqual('aa', a, )

    def test_12_get_dict(self):
        """获取值类型 dict"""
        a = get_conf('disks.disk1', file=self.conf_json)
        self.assertIsInstance(a, dict, f'类型错误实际为:{type(a)}, 期待 dict')

    def test_13_get_list(self):
        """获取值类型 list"""
        a = get_conf('lists', file=self.conf_json)
        self.assertIsInstance(a, list, f'类型错误实际为:{type(a)}, 期待 list')

    def test_14_get_null(self):
        """获取一个不存在的键"""
        a = get_conf('u_null')
        self.assertEqual(None, a, )

    def test_21_set_str(self):
        """改变一个键"""
        key, value = 'disks.disk1.Client_ID', 'Change a Key Value'
        set_conf(key, value, file=self.conf_json)
        self.assertEqual(value, get_conf(key, file=self.conf_json), f'没找到预期的结果')

    def test_22_set_str_new(self):
        """设置一个新的键到文件"""
        key, value = 'disks.disk1.Client_ID_', 'Set a New Key Value'
        set_conf(key, value, file=self.conf_json)
        self.assertEqual(value, get_conf(key, file=self.conf_json), f'没找到预期的结果')

    def test_23_set_dict(self):
        key, value = 'disks.disk1', {'a': 1}
        set_conf(key, value, file=self.conf_json)
        self.assertEqual(value, get_conf(key, file=self.conf_json), f'没找到预期的结果')

    def test_24_set_dict_new(self):
        key, value = 'disks.disk1.Client_ID_', {'a': 3}
        set_conf(key, value, file=self.conf_json)
        self.assertEqual(value, get_conf(key, file=self.conf_json), f'没找到预期的结果')

    def test_25_set_list_new(self):
        key, value = 'disks.disk1.Client_ID_', ['a', 3]
        set_conf(key, value, file=self.conf_json)
        self.assertEqual(value, get_conf(key, file=self.conf_json), f'没找到预期的结果')


class CommonZipPath(unittest.TestCase):
    """测试 zip.py"""
    origin_path = PATH_UT_RESOURCES.joinpath('zip_path')
    test_path = PathCompress(PATH_UT_RESOURCES).joinpath('zip_path')
    content = r"""{"disks":{"disk1":{"Client_ID":"aa","Client_Sea":"bb","token_cache":"cc","Client_ID_":["a",3]}}}"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.origin_len = len(cls.content)
        cls.compress_len = len(compress(cls.content.encode(), level=9))

    def tearDown(self) -> None:
        self.test_path.unlink(missing_ok=True)

    # def base_write(self, test_method_write, test_data):
    #     test_method_write()

    def test_1_compress(self):
        """压缩方法测试"""
        self.test_path.compress(self.content.encode())
        self.assertEqual(self.compress_len, self.test_path.read_bytes().__len__())
        # self.assertEqual(self.content, decompress(self.origin_path.read_bytes()).decode())

    def test_2_decompress(self):
        """解压缩方法测试"""
        self.origin_path.write_bytes(compress(self.content.encode(), level=5))  # 构建原始数据
        print(type(self.test_path.decompress()))
        self.assertEqual(self.content, self.test_path.decompress(), "解压失败")  # 解压并比对

    def test_30_write_bytes_origin(self):
        """无压缩的写入文件"""
        self.test_path.write_bytes(self.content.encode(), compress_=False)
        self.assertEqual(self.content.encode(), self.origin_path.read_bytes(), f'失败: ')

    @unittest.expectedFailure
    def test_301_write_bytes_true(self):
        """有压缩的写入文件"""
        self.test_path.write_bytes(self.content.encode(), compress_=False, level=8)
        self.assertEqual(self.content.encode(), decompress(self.origin_path.read_bytes()), f'失败: ')

    def test_31_write_bytes_true(self):
        """有压缩的写入文件"""
        self.test_path.write_bytes(self.content.encode(), compress_=True, level=8)
        self.assertEqual(self.content.encode(), decompress(self.origin_path.read_bytes()), f'失败: ')

    def test_3_write_bytes(self):
        """原始的write_bytes 是否正常"""
        _case = [
            ('Compress_5', True, 5),
            ('Compress_9', True, 9),
        ]
        for msg, compress_, level in _case:
            self.tearDown()
            with self.subTest(msg=msg, compress_=compress_, level=level):
                self.test_path.write_bytes(self.content.encode(), compress_=compress_, level=level)
                self.assertEqual(self.content.encode(), decompress(self.origin_path.read_bytes()),
                                 f'失败: {compress_=}, {level=}')

    def test_4_write_text(self):
        self.test_path.write_text(self.content, compress_=False, encoding='utf8')
        self.assertEqual(self.content, self.origin_path.read_text(), f'失败: ')

    def test_50_read_bytes_origin(self):
        """读取不压缩的二进制信息"""
        _bytes = self.content.encode()
        self.origin_path.write_bytes(_bytes)
        self.assertEqual(_bytes, self.test_path.read_bytes())

    def test_51_read_bytes_compressed(self):
        """读取压缩后的二进制信息, 并解压"""
        _bytes = self.content.encode()
        self.origin_path.write_bytes(compress(_bytes, 5))
        self.assertEqual(_bytes, self.test_path.read_bytes(decompress_=True))

    def test_52_read_bytes_compressed(self):
        """读取压缩后的二进制信息, 不解压"""
        _bytes = self.content.encode()
        self.origin_path.write_bytes(_bytes)
        self.assertEqual(_bytes, self.test_path.read_bytes())

    def test_6_read_text(self):
        self.origin_path.write_bytes(compress(self.content.encode(), level=9))
        self.assertEqual(self.content, self.test_path.read_text(decompress_=True))


class CommonSetDisk(unittest.TestCase):
    """设置Disk信息"""

    def test_set_token(self):
        pass
