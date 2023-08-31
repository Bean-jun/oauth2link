"""
MIT License

Copyright (c) 2023 Bean-jun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import requests
from flask import g
from flask.wrappers import Request
from oauth2link import utils
from oauth2link.callback import GitHubCallBackHandler
from oauth2link.types import PlatformType

from .platform import BaseOauth2Impl


class GitHubAccessApi:
    BASE_API = "https://api.github.com"
    OAUTH_API = "https://github.com/login/oauth"  # oauth2接口
    GET_USER_INFO_API = BASE_API + "/user"  # 获取用户信息接口


class GitHubOauth2(BaseOauth2Impl):
    """
    GitHub授权平台
    """
    DEFAULT_PREFIX = "LINKS_GITHUB_"
    DEFAULT_CONFIG = {
        "client_id": "",  # 客户端ID
        "response_type": "code",  # 授权类型
        "redirect_uri": "",  # 重定向地址
        "scope": "user:email",  # 授权范围
        "client_secret": "",  # 客户端秘钥
    }
    CALLBACK_HANDLER = GitHubCallBackHandler
    API = GitHubAccessApi
    Type = PlatformType.GitHub

    def redirect_url(self) -> str:
        arg_list = ["client_id",]
        full_url = "%s/authorize?%s" % (self.API.OAUTH_API,
                                        self.make_url(arg_list))
        return full_url

    def get_access_token(self, req: Request) -> dict:
        arg_list = ["client_id", "client_secret"]
        full_url = "%s/access_token?%s&accept=:json&code=%s" % (self.API.OAUTH_API,
                                                                self.make_url(
                                                                    arg_list),
                                                                self.get_callback_code(req))
        resp = requests.post(full_url, headers={"accept": 'application/json'})
        resp_dict = utils.parse_json(resp.json(), "access_token", (
            "access_token",
        ))
        setattr(g, "_%s" % self.name, resp_dict)
        return resp_dict

    def get_user_info(self):
        return self.get_user_info_by_token(self.get_token())

    def get_user_info_by_token(self, token: str) -> dict:
        """
        获取用户信息
        """
        resp = requests.get(self.API.GET_USER_INFO_API, headers={
            "Authorization": "Bearer " + token,
            "accept": 'application/json'
        })
        resp_dict = utils.parse_json(resp.json(), "id", (
            "id",
            "login",
            "avatar_url",
        ))
        origin_dict = getattr(g, "_%s" % self.name, {})
        origin_dict.update(resp_dict)
        setattr(g, "_%s" % self.name, origin_dict)
        return resp.json()

    def get_username(self):
        return self.get_info("login")
