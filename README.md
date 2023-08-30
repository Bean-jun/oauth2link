## oauth2-tools

让你的网站平台通过第三方平台快速登录授权,目前支持的平台有：

|||
| :---- | ----: | 
**新浪微博** | **GitHub** 


### 一、快速入门

1. 安装项目包

    ```shell
    git clone 本项目
    python setup.py install
    ```

2. 在项目中填写配置文件

    以微博为例：
    ```shell
    LINKS_WEIBO_CLIENT_ID
    LINKS_WEIBO_REDIRECT_URI
    LINKS_WEIBO_SCOPE
    LINKS_WEIBO_CLIENT_SECRET
    ```

    以github为例:
    ```shell
    LINKS_GITHUB_CLIENT_ID
    LINKS_GITHUB_REDIRECT_URI
    LINKS_GITHUB_SCOPE
    LINKS_GITHUB_CLIENT_SECRET
    ```

3. 导入本包并初始化&编写回调逻辑(默认的回调逻辑应该是不满足业务需求的)

    ```python
    from oauth2tools.platform import WeiBoOauth2
    from oauth2tools.callback import BaseCallBackHandler


    class MyCallBackHandler(BaseCallBackHandler):

        def do_call(self):
            self.oauth_client.get_access_token(request)
            self.oauth_client.get_user_info()
            self.oauth_client.save_model()
            ...


    links = WeiBoOauth2()
    links.CALLBACK_HANDLER = MyCallBackHandler
    links.init_app(app)
    ```

4. 编写授权跳转页面

    ```python
    from flask import redirect

    @app.get("/wei_login")
    def weibo_login():
        return redirect(links.redirect_url())
    ```


### 二、TODO

- [√] 实现多平台兼容运行

- [ ] 纳入更多支持oauth2的第三方平台