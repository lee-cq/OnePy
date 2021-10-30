#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : base
@Author     : LeeCQ
@Date-Time  : 2021/8/4 20:41

为了解耦, disk对象和item对象
"""
import abc


class DiskBase(abc.ABC):
    """磁盘基类, 适用于可拓展的disk对象.

    Disk 的操作始终着眼于一个Item对象,
    """

    @abc.abstractmethod
    def api_client(self, uri, *args, **kwargs):
        """API 请求入口"""

    @abc.abstractmethod
    def upload(self):
        pass

    @abc.abstractmethod
    def download(self):
        pass


class MSURI:
    """微软Graph API 集合."""

    ENDPOINT_1 = 'https://graph.microsoft.com/v1.0'
    ENDPOINT_BETA = 'https://graph.microsoft.com/beta'

    ENDPOINT = ENDPOINT_1

    @staticmethod
    def join_children(url: str):
        return url + ':/children' if ':' in url and not url.endswith(':') else '/children'

    class OnedriveAPI:
        # https://docs.microsoft.com/zh-cn/graph/api/drive-get?view=graph-rest-beta&tabs=http
        drive_for_me = 'GET', '/me/drive'  # 个人的驱动器信息
        drive_by_username = 'GET', '/users/{username}/drive'  # 通过UserPrincipalName 访问驱动器信息
        drive_by_groupId = 'GET', '/groups/{groupId}/drive'  # 通过GroupID获取组的驱动器信息
        drive_by_siteId = 'GET', '/sites/{siteId}/drive'  # 通过SiteId 获取SharePoint站点的驱动器信息
        drive_by_driveId = 'GET', '/drives/{driveId}'

        # https://docs.microsoft.com/zh-cn/graph/api/drive-list?view=graph-rest-beta&tabs=http
        drives_for_me = 'GET', '/me/drives'
        drives_by_groupId = 'GET', '/groups/{groupId}/drives'  # 通过GroupID枚举组的驱动器
        drives_by_siteId = 'GET', '/sites/{siteId}/drives'  # 通过SiteId枚举站点的驱动器

        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-list-children?view=graph-rest-beta&tabs=http
        children_root_for_me = 'GET', '/me/drive/root/children'
        children_root_by_driveId = 'GET', '/drives/{driveId}/root/children'
        children_root_by_groupId = 'GET', '/drives/{groupId}/root/children'
        children_root_by_siteId = 'GET', '/sites/{siteId}/drive/root/children'

        children_items_for_me = 'GET', '/me/drive/items/{itemId}/children'
        children_items_by_driveId = 'GET', '/drives/{driveId}/items/{itemId}/children'
        children_items_by_groupId = 'GET', '/groups/{groupId}/drive/items/{itemId}/children'
        children_items_by_siteId = 'GET', '/sites/{siteId}/drive/items/{itemId}/children'

        # https://docs.microsoft.com/zh-cn/graph/api/drive-recent?view=graph-rest-beta&tabs=http
        recent_file_for_me = 'GET', '/me/drive/recent'  # 个人驱动器下常用的文件

        # 获取DriveItem
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-get?view=graph-rest-beta&tabs=http
        item_for_me_with_itemId = 'GET', '/me/drive/items/{itemId}'
        item_for_me_with_itemPath = 'GET', '/me/drive/root:/{itemPath}'

        item_by_driveId_with_itemId = 'GET', '/drives/{driveId}/items/{itemId}'
        item_by_driveId_with_itemPath = 'GET', '/drives/{driveId}/root:/{itemPath}'

        item_by_groupId_with_itemId = 'GET', '/groups/{groupId}/drive/items/{itemId}'
        item_by_groupId_with_itemPath = 'GET', '/groups/{groupId}/drive/root:/{itemPath}'

        item_by_siteId_with_itemId = 'GET', '/sites/{siteId}/drive/items/{itemId}'
        item_by_siteId_with_itemPath = 'GET', '/sites/{siteId}/drive/root:/{itemPath}'

        item_by_userId_with_itemId = 'GET', '/users/{userId}/drive/items/{itemId}'
        item_by_userId_with_itemPath = 'GET', '/users/{userId}/drive/root:/{itemPath}'

        # 获取缩略图 只需要在后面增加一个 /thumbnails
        _ = 'GET', '/drives/{drive-id}/items/{item-id}/thumbnails'
        _ = 'GET', '/groups/{group-id}/drive/items/{item-id}/thumbnails'
        _ = 'GET', '/me/drive/items/{item-id}/thumbnails'
        _ = 'GET', '/sites/{site-id}/drive/items/{item-id}/thumbnails'
        _ = 'GET', '/users/{user-id}/drive/items/{item-id}/thumbnails'

        # 签出 driveItem 资源，以防止其他人编辑该文档，并在 签入所记录的文档之前阻止您的更改可见。
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-checkout?view=graph-rest-beta&tabs=http
        _ = 'POST', '/drives/{driveId}/items/{itemId}/checkout'
        _ = 'POST', '/groups/{groupId}/drive/items/{itemId}/checkout'
        _ = 'POST', '/me/drive/items/{item-id}/checkout'
        _ = 'POST', '/sites/{siteId}/drive/items/{itemId}/checkout'
        _ = 'POST', '/users/{userId}/drive/items/{itemId}/checkout'

        # 签入文件:签入已签出的 driveItem 资源，使其他用户可以使用该文档的版本。
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-checkin?view=graph-rest-beta&tabs=http
        _ = 'POST', '/drives/{driveId}/items/{itemId}/checkin'
        _ = 'POST', '/groups/{groupId}/drive/items/{itemId}/checkin'
        _ = 'POST', '/me/drive/items/{item-id}/checkin'
        _ = 'POST', '/sites/{siteId}/drive/items/{itemId}/checkin'
        _ = 'POST', '/users/{userId}/drive/items/{itemId}/checkin'

        # 新建文件夹
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-post-children?view=graph-rest-beta&tabs=http
        _ = 'POST', '/drives/{drive-id}/items/{parent-item-id}/children'
        _ = 'POST', '/groups/{group-id}/drive/items/{parent-item-id}/children'
        _ = 'POST', '/me/drive/items/{parent-item-id}/children'
        _ = 'POST', '/sites/{site-id}/drive/items/{parent-item-id}/children'
        _ = 'POST', '/users/{user-id}/drive/items/{parent-item-id}/children'

        # 按 ID 或路径更新 DriveItem 元数据。
        # 还可以通过更新项的 parentReference 属性，使用更新将 项移动到其他父级。
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-update?view=graph-rest-beta&tabs=http
        _ = 'PATCH', '/drives/{drive-id}/items/{item-id}'
        _ = 'PATCH', '/groups/{group-id}/drive/items/{item-id}'
        _ = 'PATCH', '/me/drive/items/{item-id}'
        _ = 'PATCH', '/sites/{site-id}/drive/items/{item-id}'
        _ = 'PATCH', '/users/{user-id}/drive/items/{item-id}'

        # 通过使用其 ID 或路径删除 DriveItem。
        # 注意，使用此方法删除项将把项移动到回收站中，而不是永久删除该项。
        # https://docs.microsoft.com/zh-cn/graph/api/driveitem-delete?view=graph-rest-beta&tabs=http
        _ = 'DELETE', '/drives/{drive-id}/items/{item-id}'
        _ = 'DELETE', '/groups/{group-id}/drive/items/{item-id}'
        _ = 'DELETE', '/me/drive/items/{item-id}'
        _ = 'DELETE', '/sites/{siteId}/drive/items/{itemId}'
        _ = 'DELETE', '/users/{userId}/drive/items/{itemId'

        #

    class SharePointAPI:
        """"""
