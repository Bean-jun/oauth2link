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
import datetime
import typing as t
import urllib.parse

from flask import Flask, g
from flask.wrappers import Request
from oauth2link.callback import BaseCallBackHandler


class Base:
    """
    Oauth2基类
    """
    DEFAULT_PREFIX = "LINKS_"
    DEFAULT_CONFIG = {
        "redirect_uri": "",  # 回调地址
    }
    CALLBACK_HANDLER = BaseCallBackHandler  # 回调处理器
    API = None  # api地址

    __TABLE = "LINKS_TABLE_NAME"    # 表名配置
    __TABLE_NAME = "link_oauths"    # 表名
    __Model = None                  # 表模型
    __DB = None                     # db对象

    def __init__(self, app=None):
        self.name = self.__module__.rsplit(".", 1)[-1]
        if app is not None:
            self.init_app(app)

    @classmethod
    def oauth_models(cls, app: Flask, table: str) -> None:
        if not (cls.__Model and cls.__DB):
            from flask_sqlalchemy import SQLAlchemy
            db = SQLAlchemy(app)

            class Oauth(db.Model):
                __tablename__ = table

                id = db.Column(db.Integer, primary_key=True)
                user = db.Column(db.Integer, comment="用户表id")
                username = db.Column(db.String(1024), comment="用户名")
                realname = db.Column(db.String(1024), comment="用户第三方名")
                source = db.Column(db.String(1024), comment="来源")
                access_token = db.Column(db.String(1024), comment="授权token")  # noqa
                avatar = db.Column(db.String(1024), comment="头像")
                expires = db.Column(db.DateTime, comment="过期时间")
                createtime = db.Column(db.DateTime, default=datetime.datetime.now)  # noqa
                modifytime = db.Column(db.DateTime, default=datetime.datetime.now)  # noqa

            with app.app_context():
                db.create_all()

            cls.__Model = Oauth
            cls.__DB = db

    def init_app(self, app: Flask):
        app_config = dict()

        for key in self.DEFAULT_CONFIG:
            _key = ("%s%s" % (self.DEFAULT_PREFIX, key)).upper()
            if _key in app.config:
                app_config[key] = app.config[_key]

        self.DEFAULT_CONFIG.update(app_config)

        if self.__TABLE in app.config:
            self.__TABLE_NAME = app.config[self.__TABLE]

        callback_url = self.get_callback_url()
        app.add_url_rule(callback_url,
                         view_func=self.CALLBACK_HANDLER.as_view(name="Oauth2_%s" % self.name,
                                                                 oauth_client=self))
        Base.oauth_models(app, self.__TABLE_NAME)

    def make_url(self, arg_list: t.List[str]) -> str:
        url = "&".join(["%s=%s" % (k, v)
                       for k, v in self.DEFAULT_CONFIG.items() if k in arg_list])
        return url

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

    def get_callback_code(self, req: Request) -> str:
        """
        获取回调code
        """
        code = req.args.get("code")
        return code

    db = property(lambda *args: Base.__DB)  # 获取db对象
    sql_session_model = property(lambda *args: Base.__Model)    # 获取表模型对象


class BaseOauth2(Base):

    Type = None  # 平台类型

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

    def get_user_info(self) -> dict:
        """
        获取用户信息
        """
        raise NotImplementedError

    def save_model(self, kwargs):
        """
        存储第三方用户信息至表中
        """
        raise NotImplementedError

    def get_model(self, kwargs):
        """
        获取第三方用户信息在表中的记录
        """
        raise NotImplementedError


class GetInfoMix:

    def get_info(self, key: str) -> str:
        """
        获取当前线程对象信息
        """
        return getattr(g, "_%s" % self.name, {}).get(key)

    def get_token(self):
        """
        获取授权token
        """
        return self.get_info("access_token")

    def get_expires(self):
        """
        获取授权过期时间
        """
        return self.get_info("expires_in") or 0

    def get_uid(self):
        """
        获取用户ID        
        """
        return self.get_info("id")

    def get_username(self):
        """
        获取用户名
        """
        return self.get_info("username")

    def get_avatar(self):
        """
        获取用户头像
        """
        return self.get_info("avatar_url")
