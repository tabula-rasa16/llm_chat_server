from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain import OpenAI, VectorDBQA
from langchain.chains import RetrievalQAWithSourcesChain

# from llm_initial.chatGLM2 import ChatGLM2
import pandas as pd

# save_directory = "FaissDB"  # 会在当前目录创建名为FaissDB的文件路径用于存储向量数据库的相关文件


# embeddings_path = '../embeddingModels/text2vec-base-chinese'

class KnowledgeBase:

    def __init__(self, embeddings_path  = '../embeddingModels/text2vec-base-chinese', save_directory = "FaissDB"):
        self.embeddings_path = embeddings_path # 初始化embeddings模型所在路径
        self.save_directory = save_directory # 初始化向量数据库保存路径
        self.embeddings = self.embeddings_init(embeddings_path) # 初始化embeddings
        self.db = None # 初始化向量数据库


    # 初始化embeddings
    def embeddings_init(self,embeddings_path):
        # 初始化embeddings
        embeddings = HuggingFaceEmbeddings(model_name = embeddings_path)
        return embeddings


    # 根据分割后的文本初始化创建向量数据库
    def db_init(self, docs):
        # FAISS数据库需要安装依赖
        # pip install sentence-transformers
        # pip install faiss-cpu  --->支持cpu运算
        self.db = FAISS.from_documents(docs, self.embeddings)
        # return db

    # 相似向量检索 参数query为用户输入的问题; db为当前数据库; k为摘取的topK的数量
    def similar_vectors_search(self, query, k):  
        # query = "纽约世界贸易中心在何时遭遇九一一恐怖袭击事件"
        docs_after_search = self.db.similarity_search(query, k = k) #可以指定摘取数量
        return docs_after_search #list
        # print(docs_after_search[0])

    # 向量数据库的保存
    def db_save(self):
        try:
            self.db.save_local(self.save_directory) #储存
            return 1
        except Exception as e:
            print("向量数据库保存失败:" + str(e))
            return -1

    # 向量数据库的加载
    def db_load(self):
        # 由于 Langchain 社区中的 FAISS 向量存储在加载时默认禁止了不安全的反序列化操作。这是出于安全性的考虑,因为 pickle 文件在某些情况下可能被恶意修改,导致执行任意代码的风险。可以设置 allow_dangerous_deserialization=True 来允许反序列化操作
        new_db = FAISS.load_local(self.save_directory, self.embeddings, allow_dangerous_deserialization=True) #从数据库存储的路径下加载数据库
        self.db = new_db
        return new_db

    # 向量数据库的数据可视化
    # 展示每一个数据帧的相关信息
    def show_vstore(self):
        vector_df = self.store_to_df(self.db)
        self.display(vector_df)

    # 将向量信息转换为数据帧,包括文件名、所在页码、文本内容
    def store_to_df(self):
        v_dict = self.db.docstore._dict
        doc_name = page_number = content = ""
        # print(v_dict)
        data_rows = []
        for i in v_dict.keys():
            # try:
            #     doc_name = v_dict[i].metadata['source'].split('/')[-1]
            # except KeyError as e:
            #     pass 
            # try:
            #     page_number = v_dict[i].metadata['page'] + 1
            # except KeyError as e:
            #     pass 
            # try:
            #     content = v_dict[i].page_content
            # except AttributeError as e:
            #     pass 
            if  'source' in v_dict[i].metadata:
                doc_name = v_dict[i].metadata['source'].split('/')[-1]
            else:
                pass
            if 'page' in v_dict[i].metadata:
                page_number = v_dict[i].metadata['page'] + 1
            else:
                pass
            if hasattr(v_dict[i], "page_content"):
                content = v_dict[i].page_content
            else:
                pass
            data_rows.append({"chunk_id": i, "document": doc_name, "page": page_number, "content": content})
        vector_df = pd.DataFrame(data_rows)
        return vector_df

    # 从向量数据库中删除文档
    ''' 删除文档
        入参：Faiss数据库store；待删除的文档document
    '''
    def delete_document(self, document):
        chunks_list = []
        try:
            vector_df = self.store_to_df(self.db)
            chunks_list = vector_df.loc[vector_df['document']==document]['chunk_id'].tolist()
        except:
            print("删除文档失败")
            return -1
        #根据列表中的chunkId删除数据
        self.db.delete(chunks_list)
        return 1

    # 更新模型的retriver
    def refresh_model(new_store):
        retriever = new_store.as_retriever()
        model = RetrievalQAWithSourcesChain.from_chain_type(llm="", chain_type="stuff", retriever=retriever)
        return model


    # 向向量数据库中添加文档
    def add_to_vstore(self, docs):
        # todo 需要对不同文档的读入做适配
        # loader = DirectoryLoader(directory, loader_cls=PyPDFLoader)
        # pages = loader.load_and_split()
        # text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        # docs = text_splitter.split_documents(pages)

        try:
            extension = FAISS.from_documents(docs, self.embeddings)
            # 将附加数据与原有数据合并
            self.db.merge_from(extension)
            return 1
        except:
            print("添加文档失败")
            return -1
        







    