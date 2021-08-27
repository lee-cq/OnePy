#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : zip_pathlib
@Author     : LeeCQ
@Date-Time  : 2021/8/5 20:07

压缩字符串
"""
import os
from typing import Optional
from zlib import compress, decompress
from pathlib import Path, WindowsPath as _WindowsPath, PosixPath as _PosixPath
from dotenv import load_dotenv

from ext import OneException

load_dotenv()


class PathCompress(Path):
    """"""

    def __new__(cls, *args, **kwargs):
        if cls is PathCompress:
            cls = WindowsPath if os.name == 'nt' else PosixPath

        # noinspection PyUnresolvedReferences
        self = cls._from_parts(args, init=False)
        if not self._flavour.is_supported:
            raise NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        return self

    def compress(self, _data, encoding=None, level=9):
        """写入压缩的文件"""
        return self.write_bytes(_data if isinstance(_data, bytes) else _data.encode(encoding=encoding),
                                compress_=True,
                                level=level
                                )

    def decompress(self, encoding=None) -> [str, bytes]:
        """解压文件返回字符串或者字节"""
        _bit = self.read_bytes(decompress_=True)
        try:
            return _bit.decode(**{"encoding": encoding} if encoding else {})
        except (SyntaxError, LookupError, TypeError):
            return _bit

    # noinspection PyTypeChecker
    def write_bytes(self, data: bytes, compress_=False, errors=None, level=9) -> int:
        """以字节模式打开文件，写入文件，然后关闭文件。 """

        # 在截断文件之前对缓冲区接口进行类型检查   Python
        view = memoryview(compress(data, level=level) if compress_ else data)
        with self.open(mode='wb', errors=errors) as f:
            return f.write(view)

    def write_text(self, data: str, encoding=None, errors=None, compress_=False, level=9) -> int:

        return self.write_bytes(data.encode(**{"encoding": encoding} if encoding else {}),
                                compress_=compress_,
                                level=level,
                                errors=errors)

    def read_bytes(self, decompress_=False, errors=None) -> bytes:
        """读取字节"""
        with self.open(mode='rb', errors=errors) as f:
            _data = f.read()
        try:
            if decompress_:
                return decompress(_data)
            else:
                raise OneException()
        except OneException:
            return _data

    def read_text(self, encoding: Optional[str] = None, errors: Optional[str] = None, decompress_=False) -> str:

        return self.read_bytes(
            decompress_=decompress_, errors=errors
        ).decode(**{"encoding": encoding} if encoding else {})

    def write_conf(self, data):
        """写配置文件"""
        return self.write_text(data,
                               encoding='gb18030',
                               compress_=False if os.environ.get('FLASK_DEBUG', False) else True,
                               level=9)

    def read_conf(self):
        """读配置文件"""
        return self.read_text(decompress_=False if os.environ.get('FLASK_DEBUG', False) else True,
                              encoding='gb18030')


class WindowsPath(_WindowsPath, PathCompress):
    """使得WindowsPath继承PathCompress"""

    __slots__ = ()  # 禁止使用 __dict__ 以提高效率


class PosixPath(_PosixPath, PathCompress):
    """使得PosixPath继承PathCompress"""

    __slots__ = ()  # 禁止使用 __dict__ 以提高效率


if __name__ == '__main__':
    PathCompress(Path())
