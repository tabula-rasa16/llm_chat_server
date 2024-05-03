from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from typing import Dict, List, Optional, Tuple, Union

import requests
import json



class ChatGLM2(LLM):
    
    # 对基类中的属性做类型注释
    # max_token: int = 10000 # 定义 max_token 属性
    # temperature: float = 0.1 # 定义 temperature 属性 
    # top_p: float = 0.9 # 定义 top_p 属性
    # history: List = []  # 定义 history 属性
    # url: str = "http://127.0.0.1:8000" # 定义 url 属性
    
    max_token: int = 10000 # 定义 max_token 属性
    temperature: float = 0.1 # 定义 temperature 属性 
    top_p: float = 0.9 # 定义 top_p 属性
    history: List = []  # 定义 history 属性
    url: str # 定义 url 属性
    
#     #LLM模型API部署的地址与端口，现先写死
#     url = "http://127.0.0.1:8000"

    # def __init__(self, top_p=0.9, temperature=0.1, max_token=10000, url="http://127.0.0.1:8000"):
    #     # 对基类进行初始化时必须传入非None
    #     super().__init__(max_token=max_token, temperature=temperature, top_p=top_p, history=[], url=url)
        # self.max_token = max_token
        # self.top_p = top_p
        # self.temperature = temperature
        # self.history = []
        # self.url = url

    @property
    def _llm_type(self) -> str:
        return "ChatGLM"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # headers中添加上content-type这个参数，指定为json格式
        headers = {'Content-Type': 'application/json'}
        data=json.dumps({
          'prompt':prompt,
          'temperature':self.temperature,
          'history':self.history,
          'max_length':self.max_token
        })
        # print("ChatGLM prompt:",prompt)
        # 调用api
        response = requests.post(self.url, headers=headers, data=data)
		# print("ChatGLM resp:",response)
        if response.status_code!=200:
            return "查询结果错误"
        resp = response.json()
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        self.history = self.history+[[None, resp['response']]]
        return resp['response']
