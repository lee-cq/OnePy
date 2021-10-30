#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : bt_onedrive
@Author     : LeeCQ
@Date-Time  : 2021/8/31 10:26
"""
# !/usr/bin/python
# coding: utf-8
# +-------------------------------------------------------------------
# | 微软家的云网盘服务
# +-------------------------------------------------------------------
# | Copyright (c) 2020-2099 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: linxiao & akai
# +-------------------------------------------------------------------
from __future__ import absolute_import, print_function, division
import datetime
import os, sys
import pickle
import re
import time

import oauthlib
import requests

BASE_PATH = "/www/server/panel"
os.chdir(BASE_PATH)
sys.path.insert(0, "class/")

import json
import public
from requests_oauthlib import OAuth2Session
import io

DEBUG = False
PROGRESS_FILE_NAME = "PROGRESS_FILE_NAME"

"""
=============OSClient===================
"""


class OSClient(object):
    _name = ""
    _title = ""
    default_backup_path = "/bt_backup/"
    backup_path = default_backup_path
    CONFIG_SEPARATOR = "|"
    config_file = "config.conf"
    delimiter = "/"
    auth = None
    error_msg = ""

    def __init__(self, load_config=True, config_file=None):
        if config_file:
            self.config_file = config_file
        self.__auth = None

        # 控制客户端是否从配置文件加载配置
        if load_config:
            data = self.get_config()
            self.init_config(data)

    #########################
    #####OS客户端自定义实现#####
    #########################

    def init_config(self, data):
        """初始化配置参数

        data: 配置文件信息
        """

        return False

    def get_config(self):
        """从配置文件读取配置信息"""

    def get_list(self, path="/"):
        """子类实现获取文件列表

        参考以下字段返回文件列表
        """
        mlist = {
            "list": [
                # 1. 文件夹
                {
                    "name": "",  # 文件名称
                    "type": None,  # type为None表示是文件夹
                },
                # 2. 文件
                {
                    "name": "",  # 文件名称
                    "download": "",
                    "size": "",  # 文件大小
                    "time": "",  # 上传时间
                }
            ],
            "path": "/",
        }
        return mlist

    def generate_download_url(self, object_name):
        """os客户端实现生成下载链接"""
        return ""

    def resumable_upload(self, *arg, **kwargs):
        """断点续传子类实现"""
        raise RuntimeError("不支持上传操作！")

    def delete_object_by_os(self, object_name):
        """OS客户端实现删除操作"""
        raise RuntimeError("文件无法被删除！")

    def get_lib(self):
        """注册计划任务"""
        return True

    #########################
    ######OS客户端通用实现######
    #########################

    def get_base_path(self):
        """根据操作系统获取运行基础路径"""
        return "/www/server/panel"

    def get_setup_path(self):
        """插件安装路径"""
        return os.path.join("plugin", self._name)

    def get_config_file(self):
        """获取配置文件路径"""

        path = os.path.join(self.get_setup_path(), self.config_file)
        return path

    def set_config(self, conf):
        """写入配置文件"""

        path = self.get_config_file()
        public.writeFile(path, json.dumps(conf));
        return True

    # 取目录路径
    def get_path(self, path):
        sep = ":"
        if path == '/': path = ''
        if path[-1:] == '/':
            path = path[:-1]
        if path[:1] != "/" and path[:1] != sep:
            path = "/" + path
        if path == '/': path = ''
        # if path[:1] != sep:
        #     path = sep + path
        try:
            from urllib.parse import quote
        except:
            from urllib import quote
        # path = quote(path)

        return path.replace('//', '/')

    def build_object_name(self, data_type, file_name):
        """根据数据类型构建对象存储名称

        :param data_type:
        :param file_name:
        :return:
        """

        import re

        prefix_dict = {
            "site": "web",
            "database": "db",
            "path": "path",
        }
        file_regx = prefix_dict.get(data_type) + "_(.+)_20\d+_\d+\."
        sub_search = re.search(file_regx, file_name)
        sub_path_name = ""
        if sub_search:
            sub_path_name = sub_search.groups()[0]
            sub_path_name += '/'

        # 构建OS存储路径
        object_name = self.backup_path + '/' + \
                      data_type + '/' + \
                      sub_path_name + \
                      file_name

        if object_name[:1] == "/":
            object_name = object_name[1:]

        return object_name

    def upload_file(self, file_name, data_type, *args, **kwargs):
        """按照数据类型上传文件

        针对 panelBackup v1.2以上调用
        :param file_name: 上传文件名称
        :param data_type: 数据类型 site/database/path
        :return: True/False
        """
        try:
            import re
            # 根据数据类型提取子分类名称
            # 比如data_type=database，子分类名称是数据库的名称。
            # 提取方式是从file_name中利用正则规则去提取。
            self.error_msg = ""

            if not file_name or not data_type:
                _error_msg = "文件参数错误。"
                print(_error_msg)
                self.error_msg = _error_msg
                return False

            file_name = os.path.abspath(file_name)
            temp_name = os.path.split(file_name)[1]
            object_name = self.build_object_name(data_type, temp_name)

            return self.resumable_upload(file_name,
                                         object_name=object_name,
                                         *args,
                                         **kwargs)
        except Exception as e:
            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += "文件上传出现错误：{}".format(str(e))
            return False

    def delete_object(self, object_name, retries=2):
        """删除对象

        :param object_name:
        :param retries: 重试次数，默认2次
        :return: True 删除成功
                其他 删除失败
        """

        try:
            return self.delete_object_by_os(object_name)
        except Exception as e:
            print("删除文件异常：")
            print(e)

        # 重试
        if retries > 0:
            print("重新尝试删除文件{}...".format(object_name))
            return self.delete_object(
                object_name,
                retries=retries - 1)
        return False

    def delete_file(self, file_name, data_type=None):
        """删除文件

        针对 panelBackup v1.2以上调用
        根据传入的文件名称和文件数据类型构建对象名称，再删除
        :param file_name:
        :param data_type: 数据类型 site/database/path
        :return: True 删除成功
                其他 删除失败
        """

        object_name = self.build_object_name(data_type, file_name)
        return self.delete_object(object_name)

    def get_function_args(self, func):
        import sys
        if sys.version_info[0] == 3:
            import inspect
            return inspect.getfullargspec(func).args
        else:
            return func.__code__.co_varnames

    def execute_by_comandline(self, args):
        """命令行或计划任务调用

        针对panelBackup._VERSION >=1.2命令行调用
        :param args: 脚本参数
        """

        try:
            import panelBackup
            client = self
            cls_args = self.get_function_args(panelBackup.backup.__init__)
            if "cron_info" in cls_args and len(args) == 5:
                cron_name = args[4]
                cron_info = {
                    "echo": cron_name
                }
                backup_tool = panelBackup.backup(cloud_object=client,
                                                 cron_info=cron_info)
            else:
                backup_tool = panelBackup.backup(cloud_object=client)
            _type = args[1];
            data = None
            if _type == 'site':
                if args[2].lower() == 'all':
                    backup_tool.backup_site_all(save=int(args[3]))
                else:
                    backup_tool.backup_site(args[2], save=int(args[3]))
                exit()
            elif _type == 'database':
                if args[2].lower() == 'all':
                    backup_tool.backup_database_all(int(args[3]))
                else:
                    backup_tool.backup_database(args[2],
                                                save=int(args[3]))
                exit()
            elif _type == 'path':
                backup_tool.backup_path(args[2], save=int(args[3]))
                exit()
            elif _type == 'upload':
                data = client.resumable_upload(args[2]);
            elif _type == 'download':
                data = client.generate_download_url(args[2]);
            # elif _type == 'get':
            #     data = client.get_files(args[2]);
            elif _type == 'list':
                path = "/"
                if len(args) == 3:
                    path = args[2]
                data = client.get_list(path);
            elif _type == 'lib':
                data = client.get_lib()
            elif _type == 'delete_file':
                result = client.delete_object(args[2]);
                if result:
                    print("文件{}删除成功。".format(args[2]))
                else:
                    print("文件{}删除失败!".format(args[2]))
            else:
                data = 'ERROR: 参数不正确!';
            if data:
                print()
                print(json.dumps(data))
        except Exception as e:
            print(e)


class UnauthorizedError(Exception):
    pass


class ObjectNotFoundError(Exception):
    pass


"""
=============OneDriveClient===================
"""


class OneDriveClient(OSClient, object):
    _title = "微软OneDrive"
    _name = "msonedrive"
    DEFAULT_STORAGE_CLASS = "Standard"
    backup_path = None
    credential_file = "credentials.json"
    user_conf = "user.conf"
    user_type = "international"

    def __init__(self, load_config=True, config_file=None):

        self.load()

        super(OneDriveClient, self).__init__(
            load_config=load_config,
            config_file=config_file
        )

    def load(self):
        credential_path = os.path.join(self.get_setup_path(), self.credential_file)
        credential = json.load(io.open(credential_path, "r", encoding="utf-8"))
        conf = self.get_config()
        if "user_type" in conf:
            self.user_type = conf["user_type"]
        self.credential = credential["onedrive-" + self.user_type]
        self.authorize_url = '{0}{1}'.format(
            self.credential['authority'],
            self.credential['authorize_endpoint'])
        self.token_url = '{0}{1}'.format(
            self.credential['authority'],
            self.credential['token_endpoint'])

        self.token_file = "token.pickle"
        self.token_path = os.path.join(self.get_setup_path(), self.token_file)
        if not os.path.exists(self.token_path):
            with io.open(self.token_path, "w"):
                pass
        self.root_uri = self.credential["api_uri"] + "/me/drive/root"

    def get_sign_in_url(self):
        """生成签名地址"""

        # Initialize the OAuth client
        aad_auth = OAuth2Session(self.credential["client_id"],
                                 scope=self.credential['scopes'],
                                 redirect_uri=self.credential['redirect_uri'])

        sign_in_url, state = aad_auth.authorization_url(self.authorize_url,
                                                        prompt='login')

        return sign_in_url, state

    def get_token_from_authorized_url(self, authorized_url, expected_state=None):
        """通过授权编码获取访问token"""

        # 忽略token scope与已请求的scope不一致
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'
        public.WriteLog("test", self.user_type)
        aad_auth = OAuth2Session(self.credential["client_id"],
                                 state=expected_state,
                                 scope=self.credential['scopes'],
                                 redirect_uri=self.credential['redirect_uri'])

        token = aad_auth.fetch_token(
            self.token_url,
            client_secret=self.credential["client_secret"],
            authorization_response=authorized_url)

        return token

    def get_user_conf(self):
        return os.path.join(self.get_setup_path(), self.user_conf)

    def get_user(self):
        """从本地获取用户信息"""
        if os.path.exists(self.get_user_conf()):
            with io.open(self.get_user_conf(), "r") as fp:
                user = fp.read().strip()
                return user

    def clear_user(self):
        try:
            # 清空user
            if os.path.isfile(self.get_user_conf()):
                os.remove(self.get_user_conf())
        except:
            if DEBUG:
                print("清除user失败。")

    def store_user(self):
        """更新并存储用户信息"""
        user = self.get_user_from_ms()
        if user:
            with io.open(self.get_user_conf(), "w") as fp:
                fp.write(user)
        else:
            raise RuntimeError("无法获取用户信息。")

    def clear_token(self):
        """清除token记录"""
        try:
            if os.path.isfile(self.token_path):
                os.remove(self.token_path)
        except:
            if DEBUG:
                print("清除token失败。")

    def store_token(self, token):
        """存储token"""
        with io.open(self.token_path, "wb") as fp:
            pickle.dump(dict(token), fp, protocol=2)

    def get_token(self):
        """获取token"""

        try:
            with io.open(self.token_path, "rb") as fp:
                if sys.version_info.major == 3:
                    token = pickle.load(fp, encoding='bytes')
                if sys.version_info.major == 2:
                    token = pickle.load(fp)
        except EOFError:
            token = None

        if token is None:
            raise UnauthorizedError("未读取到授权信息，请先对插件授权之后再试。")

            # if DEBUG:
            #     print("Token debug:")
            #     print(token)

        now = time.time()
        expire_time = token["expires_at"] - 300
        if now >= expire_time:
            new_token = self.refresh_token(token)
            self.store_token(new_token)
            return new_token
        return token

    def refresh_token(self, origin_token):
        """刷新token"""

        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'
        refresh_token = origin_token["refresh_token"]
        aad_auth = OAuth2Session(
            self.credential["client_id"],
            scope=self.credential["scopes"],
            redirect_uri=self.credential["redirect_uri"])

        new_token = aad_auth.refresh_token(
            self.token_url,
            refresh_token=refresh_token,
            client_id=self.credential["client_id"],
            client_secret=self.credential["client_secret"])

        return new_token

    def clear_auth(self):
        self.clear_token()
        self.clear_user()

    def init_config(self, data):
        """初始化配置文件"""

        if not data:
            return

        bp = data.get("backup_path").strip()

        if bp != "/":
            bp = self.get_path(bp)
        if bp:
            self.backup_path = bp
        else:
            self.backup_path = self.default_backup_path

    def get_user_from_ms(self):
        """查询用户信息"""
        try:
            headers = self.get_authorized_header()
            user_api_base = self.credential["api_uri"] + "/me"
            # select_user_info_uri = self.build_uri(base=user_api_base)
            response = requests.get(user_api_base, headers=headers)
            if DEBUG:
                print("Debug get user:")
                print(response.status_code)
                print(response.text)
            if response.status_code == 200:
                response_data = response.json()
                user_principal_name = response_data["userPrincipalName"]
                return user_principal_name
        except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
            self.clear_auth()
            if DEBUG:
                print("用户授权已过期。")
        return None

    def get_config(self):
        """获取配置参数"""
        default_config = {
            "backup_path": self.default_backup_path,
        }

        try:
            path = self.get_config_file()
            conf_obj = default_config
            if os.path.exists(path):
                conf = public.readFile(path)
                conf_obj = json.loads(conf)

            try:
                conf_obj["sign_url"] = self.get_sign_in_url()[0]
            except:
                conf_obj["sign_url"] = ""
            conf_obj["user"] = self.get_user()
            if "user_type" not in conf_obj:
                conf_obj["user_type"] = self.user_type
            return conf_obj
        except RuntimeError:
            return None

    def authorize(self):
        return None

    def resumable_upload(self,
                         local_file_name,
                         object_name=None,
                         progress_callback=None,
                         progress_file_name=None,
                         multipart_threshold=1024 * 1024 * 2,
                         part_size=1024 * 1024 * 5,
                         store_dir="/tmp",
                         auto_cancel=True,
                         retries=5,
                         ):
        """断点续传

        :param local_file_name: 本地文件名称
        :param object_name: 指定OS中存储的对象名称
        :param part_size: 指定分片上传的每个分片的大小。必须是320*1024的整数倍。
        :param multipart_threshold: 文件长度大于该值时，则用分片上传。
        :param progress_callback: 进度回调函数，默认是把进度信息输出到标准输出。
        :param progress_file_name: 进度信息保存文件，进度格式参见[report_progress]
        :param store_dir: 上传分片存储目录, 默认/tmp。
        :param auto_cancel: 当备份失败是否自动取消上传记录
        :param retries: 上传重试次数
        :return: True上传成功/False or None上传失败
        """

        try:
            file_size_separation_value = 4 * 1024 * 1024
            if part_size % 320 != 0:
                if DEBUG:
                    print("Part size 必须是320的整数倍。")
                return False

            if object_name is None:
                temp_file_name = os.path.split(local_file_name)[1]
                object_name = os.path.join(self.backup_path, temp_file_name)

            # if progress_file_name:
            #     os.environ[PROGRESS_FILE_NAME] = progress_file_name
            #     progress_callback = report_progress

            print("|-正在上传到 {}...".format(object_name))
            dir_name = os.path.split(object_name)[0]
            if not self.create_dir(dir_name):
                if DEBUG:
                    print("目录创建失败！")
                return False

            local_file_size = os.path.getsize(local_file_name)
            # if local_file_size < file_size_separation_value:
            if False:
                # 小文件上传
                upload_uri = self.build_uri(path=object_name,
                                            operate="/content")
                if DEBUG:
                    print("Upload uri:")
                    print(upload_uri)
                headers = self.get_authorized_header()
                # headers.update({
                #     "Content-Type": "application/octet-stream"
                # })
                # files = {"file": (object_name, open(local_file_name, "rb"))}
                file_data = open(local_file_name, "rb")
                response = requests.put(upload_uri,
                                        headers=headers,
                                        data=file_data)
                if DEBUG:
                    print("status code:")
                    print(response.status_code)
                    # print(response.text)
                if response.status_code in [201, 200]:
                    if DEBUG:
                        print("文件上传成功！")
                    return True
            else:
                # 大文件上传

                # import hashlib
                # file_identity = hashlib.md5(os.path.abspath(local_file_name).decode("utf-8")).hexdigest()
                # _path = public.M('config').where("id=?",(1,)).getField('backup_path')
                # upload_log_dir = os.path.join(_path, "msonedrive_upload_log")
                # if not os.path.exists(upload_log_dir):
                #     os.mkdir(upload_log_dir)
                # upload_log_file = os.path.join(upload_log_dir, file_identity)
                # if os.path.isfile(upload_log_file):
                #     try:
                #         with open(upload_log_file, "r") as fp:
                #             log_data = json.load(fp)
                #             upload_url = log_data.get("upload_url")
                #             expiration_date_time = log_data.get("expiration_date_time")

                # 1. 创建上传session
                create_session_uri = self.build_uri(
                    path=object_name,
                    operate="createUploadSession")
                headers = self.get_authorized_header()
                response = requests.post(create_session_uri, headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    upload_url = response_data["uploadUrl"]
                    expiration_date_time = response_data["expirationDateTime"]

                    if DEBUG:
                        print("上传session已建立。")
                        print("Upload url: {}".format(upload_url))
                        print("Expiration datetime: {}".format(expiration_date_time))

                    # 2. 分片上传文件
                    requests.adapters.DEFAULT_RETRIES = 1
                    session = requests.session()
                    session.keep_alive = False

                    # 开始分片上传
                    import math
                    parts = int(math.ceil(local_file_size / part_size))
                    for i in range(parts):
                        if DEBUG:
                            if i == parts - 1:
                                num = "最后"
                            else:
                                num = "第{}".format(i + 1)
                            print("正在上传{}部分...".format(num))

                        upload_range_start = i * part_size
                        upload_range_end = min(upload_range_start + part_size,
                                               local_file_size)
                        content_length = upload_range_end - upload_range_start

                        headers = {
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                                          'Chrome/67.0.3396.99 Safari/537.36'
                        }
                        # 开发记录
                        # Content-Range和标准的http请求头中的Range作用有所不同
                        # Content-Range是OneDrive自定义的分片上传标识，格式也不一样
                        headers.update({
                            "Content-Length": repr(content_length),
                            "Content-Range": "bytes {}-{}/{}".format(
                                upload_range_start,
                                upload_range_end - 1,
                                local_file_size),
                            "Content-Type": "application/octet-stream"
                        })

                        if DEBUG:
                            print("Headers:")
                            print(headers)

                        # TODO 优化read的读取占用内存
                        f = io.open(local_file_name, "rb")
                        f.seek(upload_range_start)
                        upload_data = f.read(content_length)
                        sub_response = session.put(upload_url,
                                                   headers=headers,
                                                   data=upload_data)

                        expected_status_code = [200, 201, 202]
                        if sub_response.status_code in expected_status_code:
                            if DEBUG:
                                print("Response status code: {}, "
                                      "bytes {}-{} 已上传成功。".format(
                                    sub_response.status_code,
                                    upload_range_start,
                                    upload_range_end - 1)
                                )
                                print(sub_response.text)
                            if sub_response.status_code in [200, 201]:
                                if DEBUG:
                                    print("文件 {} 上传成功。".format(object_name))
                                return True
                        else:
                            print(sub_response.status_code)
                            print(sub_response.text)
                            _error_msg = "Bytes {}-{} 分片上传失败。".format(
                                upload_range_start,
                                upload_range_end
                            )
                            if self.error_msg:
                                self.error_msg += r"\n"
                            self.error_msg += _error_msg
                            raise RuntimeError(_error_msg)

                        time.sleep(0.5)
                else:
                    raise RuntimeError("session创建失败。")

        except UnauthorizedError as e:
            _error_msg = str(e)
            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += _error_msg
            print(_error_msg)
            return False
        except Exception as e:
            print("文件上传出现错误：")
            print(e)

            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += "文件{}上传出现错误：{}".format(object_name, str(e))

            try:
                if upload_url:
                    if DEBUG:
                        print("正在清理上传session.")
                    session.delete(upload_url)
            except:
                pass
        finally:
            try:
                f.close()
            except:
                pass
            try:
                session.close()
            except:
                pass

        # 重试断点续传
        if retries > 0:
            print("重试上传文件....")
            return self.resumable_upload(
                local_file_name,
                object_name=object_name,
                store_dir=store_dir,
                part_size=part_size,
                multipart_threshold=multipart_threshold,
                progress_callback=progress_callback,
                progress_file_name=progress_file_name,
                retries=retries - 1,
            )
        else:
            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += "文件{}上传失败。".format(object_name)
        return False

    def get_authorized_header(self):
        token_obj = self.get_token()
        token = token_obj["access_token"]
        header = {
            "Authorization": "Bearer " + token,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36'
        }
        return header

    def build_uri(self, path="", operate=None, base=None):
        """构建请求URL

        API请求URI格式参考:
            https://graph.microsoft.com/v1.0/me/drive/root:/bt_backup/:content
            ---------------------------------------------  ---------- --------
                                  base                        path    operate
        各部分之间用“：”连接。
        :param path 子资源路径
        :param operate 对文件进行的操作，比如content,children
        :return 请求url
        """

        if base is None:
            base = self.root_uri
        path = self.get_path(path)
        sep = ":"
        if operate:
            if operate[:1] != "/":
                operate = "/" + operate

        if path:
            uri = base + sep + path
            if operate:
                uri += sep + operate
        else:
            uri = base
            if operate:
                uri += operate

        return uri

    def get_list(self, path="/"):
        """获取存储空间中的所有文件对象"""

        list_uri = self.build_uri(path, operate="/children")
        if DEBUG:
            print("List uri:")
            print(list_uri)

        data = []
        response = requests.get(list_uri, headers=self.get_authorized_header())
        status_code = response.status_code
        if status_code == 200:
            if DEBUG:
                print("DEBUG:")
                print(response.json())
            response_data = response.json()
            drive_items = response_data["value"]

            for item in drive_items:
                tmp = {}
                tmp['name'] = item["name"]
                tmp['size'] = item["size"]
                if "folder" in item:
                    # print("{} is folder:".format(item["name"]))
                    # print(item["folder"])
                    tmp["type"] = None
                    tmp['download'] = "";
                if "file" in item:
                    tmp["type"] = "File"
                    tmp['download'] = item["@microsoft.graph.downloadUrl"];
                    # print("{} is file:".format(item["name"]))
                    # print(item["file"])

                formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]
                t = None
                for time_format in formats:
                    try:
                        t = datetime.datetime.strptime(
                            item["lastModifiedDateTime"], time_format)
                        break
                    except:
                        continue
                t += datetime.timedelta(hours=8)
                ts = int(
                    (time.mktime(t.timetuple()) + t.microsecond / 1000000.0))
                tmp['time'] = ts
                data.append(tmp)

        mlist = {'path': path, 'list': data}
        return mlist

    def create_dir(self, dir_name):
        """创建远程目录

        # API 请求结构
        # POST /me/drive/root/children
        # or
        # POST /me/drive/root:/bt_backup/:/children
        # Content - Type: application / json

        # {
        #     "name": "New Folder",
        #     "folder": {},
        #     "@microsoft.graph.conflictBehavior": "rename"
        # }

        # Response: status code == 201 新创建/ 409 已存在
        # @microsoft.graph.conflictBehavior: fail/rename/replace

        :param dir_name: 目录名称
        :param parent_id: 父目录ID
        :return: True/False
        """

        dir_name = self.get_path(dir_name.strip())
        onedrive_business_reserved = r"[\*<>?:|#%]"
        if re.search(onedrive_business_reserved, dir_name) \
                or dir_name[-1] == "." or dir_name[:1] == "~":
            if DEBUG:
                print("文件夹名称包含非法字符。")
            return False

        parent_folder = self.get_path(os.path.split(dir_name)[0])
        sub_folder = os.path.split(dir_name)[1]

        obj = self.get_object(dir_name)
        # 判断对象是否存在
        if obj is None:
            if not self.create_dir_by_step(parent_folder, sub_folder):

                # 兼容OneDrive 商业版文件夹创建
                folder_array = dir_name.split("/")
                parent_folder = self.get_path(folder_array[0])
                for i in range(1, len(folder_array)):
                    sub_folder = folder_array[i]
                    if DEBUG:
                        print("Parent folder: {}".format(parent_folder))
                        print("Sub folder: {}".format(sub_folder))
                    if self.create_dir_by_step(parent_folder, sub_folder):
                        parent_folder += "/" + folder_array[i]
                    else:
                        return False
            return True
        else:
            if self.is_folder(obj):
                if DEBUG:
                    print("文件夹已存在。")
                return True

    def create_dir_by_step(self, parent_folder, sub_folder):
        create_uri = self.build_uri(path=parent_folder, operate="/children")

        if DEBUG:
            print("Create dir uri:")
            print(create_uri)
        post_data = {
            "name": sub_folder,
            "folder": {"@odata.type": "microsoft.graph.folder"},
            "@microsoft.graph.conflictBehavior": "fail"
        }

        headers = self.get_authorized_header()
        headers.update({"Content-type": "application/json"})
        response = requests.post(create_uri, headers=headers, json=post_data)
        if response.status_code in [201, 409]:
            if DEBUG:
                if response.status_code == 409:
                    print("目录：{} 已经存在。".format(sub_folder))
            return True
        else:
            if DEBUG:
                print("目录：{} 创建失败：".format(sub_folder))
                print(response.status_code)
                print(response.text)
        return False

    def download_file(self,
                      object_name,
                      file_name,
                      progress_file_name=None,
                      progress_callback=None,
                      multiget_threshold=1024 * 1024 * 2,
                      part_size=1024 * 1024 * 2,
                      store_dir="/tmp",
                      retries=2):
        """文件下载

        :param object_name: OS中存储的对象名称
        :param file_name: 存储到本地的文件名称
        :param part_size: 分片下载的每个分片的大小。如不指定，则自动计算。
        :param multiget_threshold: 文件长度大于该值时，则用分片下载。
        :param progress_callback: 进度回调函数，默认是把进度信息输出到标准输出。
        :param progress_file_name: 进度信息保存文件，进度格式参见[report_progress]
        :param store_dir: 下载分片存储目录
        :param retries: 下载重试次数
        :return: True下载成功/False or None下载失败
        :raises NoSuchKey: 对象不存在错误。
                OsError: 与OS平台相关的错误
                RuntimeError: 出现其他未知错误，触发重试机制之后抛出。
        """
        try:
            pass
        except Exception as e:
            print("下载文件{}出现错误:".format(object_name) + str(e))

        if retries > 0:
            return self.download_file(object_name,
                                      file_name,
                                      progress_file_name=progress_file_name,
                                      progress_callback=progress_callback,
                                      multiget_threshold=multiget_threshold,
                                      part_size=part_size,
                                      store_dir=store_dir,
                                      retries=retries - 1)
        return False

    def get_object(self, object_name):
        """查询对象信息"""
        try:
            get_uri = self.build_uri(path=object_name)
            if DEBUG:
                print("Get uri:")
                print(get_uri)
            response = requests.get(get_uri,
                                    headers=self.get_authorized_header())
            if response.status_code in [200]:
                response_data = response.json()
                if DEBUG:
                    print("Object info:")
                    print(response_data)
                return response_data
            if response.status_code == 404:
                if DEBUG:
                    print("对象不存在。")
            if DEBUG:
                print("Get Object debug:")
                print(response.status_code)
                print(response.text)
        except Exception as e:
            if DEBUG:
                print("Get object has excepiton:")
                print(e)
        return None

    def generate_download_url(self, object_name, expires=60 * 60):
        """生成下载url

        :param object_name: 对象名称
        :param expires: 过期时间（单位：秒），默认1小时。
        :return: 签名URL。
        """
        try:
            response_data = self.get_object(object_name)
            if response_data:
                standard_url = response_data["@microsoft.graph.downloadUrl"]
                return standard_url
            return ""
        except Exception as e:
            raise RuntimeError("查询下载链接出现错误:" + str(e))

    def is_folder(self, obj):
        if "folder" in obj:
            return True
        return False

    def delete_object_by_os(self, object_name):
        """删除对象

        :param object_name:
        :return: True 删除成功
                其他 删除失败
        """
        obj = self.get_object(object_name)
        if obj is None:
            if DEBUG:
                print("对象不存在，删除操作未执行。")
            return True
        if self.is_folder(obj):
            child_count = obj["folder"]["childCount"]
            if child_count > 0:
                if DEBUG:
                    print("文件夹不是空文件夹无法删除。")
                return False

        headers = self.get_authorized_header()
        delete_uri = self.build_uri(object_name)
        response = requests.delete(delete_uri, headers=headers)
        if response.status_code == 204:
            if DEBUG:
                print("对象: {} 已被删除。".format(object_name))
            return True
        return False

    def change_user_type(self, user_type):
        if not user_type:
            user_type = "international"
        public.WriteLog("test2", user_type)
        self.user_type = user_type
        conf_obj = self.get_config()
        conf_obj["user_type"] = self.user_type
        self.set_config(conf_obj)
        self.load()
        return self.get_sign_in_url()


class msonedrive_main:
    _client = None

    def __init__(self):
        try:
            self.get_lib()
        except:
            pass

    @property
    def client(self):
        if self._client is None:
            self._client = OneDriveClient()
        return self._client

    def get_config(self, get):
        return self.client.get_config()

    def set_config(self, get):
        backup_path = get.backup_path
        conf_obj = {
            "backup_path": backup_path,
        }
        try:
            if self.client.set_config(conf_obj):
                return public.returnMsg(True, "配置修改成功！")
        except:
            pass
        return public.returnMsg(False, "配置修改失败！")

    # 创建目录
    def create_dir(self, get):
        try:
            path = get.path + "/" + get.dirname;
            if self.client.create_dir(path):
                return public.returnMsg(True, '创建成功!');
            else:
                return public.returnMsg(False, "创建失败！")
        except KeyError as e:
            return public.returnMsg(False, "目录创建失败:" + str(e))

    # 获取列表
    def get_list(self, get):
        try:
            return self.client.get_list(get.path)
        except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
            self.client.clear_auth()
            return public.returnMsg(False, "授权失效。")
        except Exception:
            return public.returnMsg(False, "获取列表失败！")

    def clear_auth(self, get):
        try:
            self.client.clear_auth()
            return public.returnMsg(True, "本地授权已撤销。")
        except:
            return public.returnMsg(False, "授权撤销失败！")

    def set_auth_url(self, get):
        try:
            url = str(get.url)
            if url.startswith("http://"):
                url = url.replace("http://", "https://")
            token = self.client.get_token_from_authorized_url(
                authorized_url=url)
            self.client.store_token(token)
            self.client.store_user()
            return public.returnMsg(True, "授权成功！")
        except Exception:
            pass
        return public.returnMsg(False, "授权失败！")

    # 删除文件
    def delete_file(self, get):
        try:
            path = get.path
            filename = get.filename
            if path[-1] != "/":
                file_name = path + "/" + filename
            else:
                file_name = path + filename

            if file_name[-1] == "/":
                return public.returnMsg(False, "暂时不支持目录删除！")

            if file_name[:1] == "/":
                file_name = file_name[1:]
            if self.client.delete_object(file_name):
                return public.returnMsg(True, '删除成功')
            return public.returnMsg(False, '文件{}删除失败！'.format(file_name))
        except:
            return public.returnMsg(False, '文件删除失败!')

    # 下载文件
    def download_file(self, filename):
        """生成下载文件链接

        从文件名反推出文件在云存储中的真实下载链接
        下载链接根据当前的存储路径拼接，如果存储路径发生过改变，链接会失效。
        :filename: 备份文件名
            格式参考：web_192.168.1.245_20200703_183016.tar.gz
        """
        import re
        _result = re.search("([^_]+)_.+", filename)
        if _result:
            file_type = _result.group(1)
            reversal_prefix_dict = {
                "web": "site",
                "db": "database",
                "path": "path",
            }
            data_type = reversal_prefix_dict.get(file_type)
            object_name = self.client.build_object_name(data_type,
                                                        filename)
            return self.client.generate_download_url(object_name)
        else:
            return filename

    def get_lib(self):
        import json
        info = {
            "name": self.client._title,
            "type": "计划任务",
            "ps": "微软家的云网盘服务。",
            "status": 'false',
            "opt": "msonedrive",
            "module": "msonedrive",
            "script": "msonedrive",
            "help": "https://www.bt.cn/bbs/thread-54124-1-1.html",
            "backup_path": "备份保存路径, 默认是/bt_backup",
            "check": [
                "/usr/lib/python2.7/site-packages/requests-oauthlib/__init__.py",
                "/www/server/panel/pyenv/bin/python3.7/site-packages/requests-oauthlib/__init__.py"
            ]
        }
        lib = '/www/server/panel/data/libList.conf'
        lib_dic = json.loads(public.readFile(lib))
        for i in lib_dic:
            if info['name'] in i['name']:
                return True
            else:
                pass
        lib_dic.append(info)
        public.writeFile(lib, json.dumps(lib_dic))
        return lib_dic

    def change_user_type(self, data):
        try:
            user_type = data.user_type
            url, _state = self.client.change_user_type(user_type)
            return public.returnMsg(True, url)
        except:
            pass
        return public.returnMsg(False, "修改账号类型失败！")


if __name__ == "__main__":

    import panelBackup

    client = OneDriveClient()
    backup_tool = panelBackup.backup(cloud_object=client)
    args = sys.argv
    if len(args) <= 1:
        sys.exit(0)

    _type = args[1]
    data = None
    if _type == 'site':
        if args[2].lower() == "all":
            backup_tool.backup_site_all(save=int(args[3]))
        else:
            backup_tool.backup_site(args[2], save=int(args[3]))
        exit()
    elif _type == 'database':
        if args[2].lower() == "all":
            backup_tool.backup_database_all(int(args[3]))
        else:
            backup_tool.backup_database(args[2],
                                        save=int(args[3]))
        exit()
    elif _type == 'path':
        backup_tool.backup_path(args[2], save=int(args[3]))
        exit()
    elif _type == 'upload':
        file_name = os.path.abspath(args[2])
        data = client.resumable_upload(file_name);
    elif _type == 'download':
        # data = client.generate_download_url(args[2]);
        data = msonedrive_main().download_file(args[2])

    # elif _type == 'get':
    #     data = client.get_files(args[2]);
    elif _type == 'list':
        path = "/"
        if len(args) == 3:
            path = args[2]
        data = client.get_list(path);
    elif _type == 'lib':
        data = client.get_lib()
    elif _type == 'delete_file':
        result = client.delete_object(args[2]);
        if result:
            print("文件{}删除成功。".format(args[2]))
        else:
            print("文件{}删除失败!".format(args[2]))
    elif _type == "create_dir":
        dir_name = sys.argv[2]
        if client.create_dir(dir_name):
            print("文件夹 {} 创建成功。".format(dir_name))
        else:
            print("文件夹 {} 创建失败。".format(dir_name))
    elif _type == "get_config":
        data = client.get_config()
    else:
        data = 'ERROR: 参数不正确!';
    if data:
        print()
        print(json.dumps(data))
