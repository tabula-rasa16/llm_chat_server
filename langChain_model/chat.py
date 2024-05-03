from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain import OpenAI, VectorDBQA
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain

from llm_initial.chatGLM2 import ChatGLM2
import pandas as pd

class Chat():

    def __init__(self, llm, max_history = 5):
        self.llm = llm
        self.max_history = max_history
        self.chat_round = 0
        self.chain = self.chain_create()
        
    # prompt初始化
    def prompt_create(self, topK_docs, query):
        context = ""
        for item in topK_docs:
            context += f"{topK_docs.index(item) + 1}. 文段内容: {item.page_content}; 文段来源: {item.metadata}\n"
        # print(context)
        # 构造prompt模板，在提示词中做限制
        prompt_template = f"""基于以下一段或多段已知的文段信息，从中提取可以回答用户问题的信息，并生成非常准确、合理、通顺的答案。请严格按照提供的文段内容进行回答。如果你无法从提供的文段中得到答案，
            请说 "根据已知信息无法回答该问题" 或 "您没有提供足够的相关信息"。
            已知文段:
            ------------------------------------------------------------------------------
                {context}
            ------------------------------------------------------------------------------
            问题:
            *************************
                {query}
            *************************
            """
            # print(prompt_template)
        return prompt_template
    
    # chain初始化
    def chain_create(self):
        # 创建内存对象,用于存储聊天历史记录
        print("*************:", self.max_history)
        memory = ConversationBufferWindowMemory(k = self.max_history)  # 保留最近的n次对话
        chain = ConversationChain(
            llm = self.llm,
            memory = memory
        )
        return chain
    

    # 问题上送与回答接收,保留max_history条历史记录
    def chat_with_llm(self, query):
        response = self.chain.run(query)
        self.chat_round += 1
        return response
   