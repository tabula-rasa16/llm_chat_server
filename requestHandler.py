import requests
class RequestHandler:
    def __init__(self):
        """session管理器"""
        self.session = requests.session()
    def visit(self, method, url, params=None, data=None, json=None, headers=None, **kwargs):
        return self.session.request(method,url, params=params, data=data, json=json, headers=headers,**kwargs)
    def close_session(self):
        """关闭session"""
        self.session.close()

if __name__ == '__main__':
    # 以下是测试代码
    # post请求接口
    url = 'http://127.0.0.1:8000/user/login/'
    payload = {
        "username": "vivi",
        "password": "123456"
    }
    req = RequestHandler()
    login_res = req.visit("post", url, json=payload)
    print(login_res.text)