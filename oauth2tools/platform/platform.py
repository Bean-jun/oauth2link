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
import typing as t
import urllib.parse
import datetime
from flask import Flask
from flask.wrappers import Request
from oauth2tools.callback import BaseCallBackHandler


class BaseOauth2:
    """
    Oauth2基类
    """
    DEFAULT_PREFIX = "LINKS_"
    DEFAULT_CONFIG = {
        "redirect_uri": "",  # 回调地址
    }
    CALLBACK_HANDLER = BaseCallBackHandler  # 回调处理器
    API = None  # api地址
    TABLE = "oauths"    # 表名

    def __init__(self, app=None):
        self.name = self.__module__.rsplit(".", 1)[-1]
        if app is not None:
            self.init_app(app)

    def oauth_models(self, app: Flask, table="oauths"):
        from flask_sqlalchemy import SQLAlchemy
        self.db = SQLAlchemy(app)

        class Oauth(self.db.Model):
            __tablename__ = table

            id = self.db.Column(self.db.Integer, primary_key=True)
            user = self.db.Column(self.db.Integer, comment="用户表id")
            username = self.db.Column(self.db.String(1024), comment="用户名")
            realname = self.db.Column(self.db.String(1024), comment="用户第三方名")
            source = self.db.Column(self.db.String(1024), comment="来源")
            access_token = self.db.Column(self.db.String(1024), comment="授权token")
            expires = self.db.Column(self.db.DateTime, comment="过期时间")
            createtime = self.db.Column(self.db.DateTime, default=datetime.datetime.now)
            modifytime = self.db.Column(self.db.DateTime, default=datetime.datetime.now)

        with app.app_context():
            self.db.create_all()
        self.sql_session_model = Oauth

    def init_app(self, app: Flask):
        app_config = dict()

        for key in self.DEFAULT_CONFIG:
            _key = ("%s%s" % (self.DEFAULT_PREFIX, key)).upper()
            if _key in app.config:
                app_config[key] = app.config[_key]

        self.DEFAULT_CONFIG.update(app_config)

        callback_url = self.get_callback_url()
        app.add_url_rule(callback_url,
                         view_func=self.CALLBACK_HANDLER.as_view(name="Oauth2_%s" % self.name,
                                                                 oauth_client=self))
        self.oauth_models(app, self.TABLE)

    def make_url(self, arg_list: t.List[str]) -> str:
        url = "&".join(["%s=%s" % (k, v)
                       for k, v in self.DEFAULT_CONFIG.items() if k in arg_list])
        return url

    def parse_json(self, json_data: dict, validated_key: str, *keys: t.List[str]) -> dict:
        """
        解析响应
        """
        if validated_key not in json_data:
            return {}

        res = {}
        for key in keys:
            if key in json_data:
                res[key] = json_data[key]
        return res

    def replace_dict_key(self, json_data: dict, replace_keys: dict) -> dict:
        """
        字典键替换
        """
        res = {}
        for k, v in json_data.items():
            if k in replace_keys:
                res[replace_keys[k]] = v
            else:
                res[k] = v
        return res

    def get_callback_url(self) -> str:
        """
        获取回调地址
        """
        callback_url = self.DEFAULT_CONFIG.get("redirect_uri")
        if not callback_url.startswith("http"):
            return callback_url
        o = urllib.parse.urlparse(callback_url)
        if o.query:
            return "%s?%s" % (o.path, o.query)
        return o.path

    def redirect_url(self) -> str:
        """
        重定向至第三方认证页面
        """
        raise NotImplementedError

    def get_access_token(self, req: Request) -> dict:
        """
        获取第三方授权token
        """
        raise NotImplementedError

    def save_model(self, kwargs):
        """
        存储第三方用户信息
        """
        raise NotImplementedError

    def get_model(self, kwargs):
        """
        获取第三方用户信息
        """
        raise NotImplementedError
