from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader, PyPDFLoader

from langchain.text_splitter import CharacterTextSplitter,MarkdownTextSplitter
from langchain.document_loaders import UnstructuredFileLoader,UnstructuredMarkdownLoader
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.document_loaders import UnstructuredImageLoader

# !pip install unstructured
# !pip install pypdf
# !pip install rapidocr_onnxruntime pdf2image pdfminer.six -i https://pypi.tuna.tsinghua.edu.cn/simple
from rapidocr_onnxruntime import RapidOCR


from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings

import os

class FileLoader:
    def __init__(self, files_path = "./documents"):
        self.files_path = files_path

# files_path = "./documents"

    # 不同格式文件的读入

    # UnstructuredFileLoader依赖unstructured 包，需要执行以下命令进行安装 pip install unstructured

    #加载txt文件
    def load_txt_file(self, txt_file):    
        # loader = UnstructuredFileLoader(os.path.join(files_path, txt_file)) #安装unstructured库后仍报错，放弃
        loader = TextLoader(os.path.join(self.files_path, txt_file))
        docs = loader.load()
        print(docs[0].page_content[:100])
        return docs

    #加载md文件
    def load_md_file(self, md_file):    
        loader = UnstructuredMarkdownLoader(os.path.join(self.files_path, md_file))
        docs = loader.load()
        print(docs[0].page_content[:100])
        return docs

    # pypdf package not found, please install it with `pip install pypdf`
    #加载pdf文件
    def load_pdf_file(self, pdf_file):    
        # loader = UnstructuredPDFLoader(os.path.join(files_path, pdf_file))
        loader = PyPDFLoader(os.path.join(self.files_path, pdf_file), extract_images=True) #用于从pdf文件中提取图片中的文本信息，需要RapidOCR库
        docs = loader.load()
        # print('pdf:\n',docs[0].page_content[:100])
        print('pdf:\n',docs)
        return docs

    #加载jpg文件
    def load_jpg_file(self, jpg_file):
        ocr = RapidOCR()
        result,_ = ocr(os.path.join(self.files_path,jpg_file))
        docs = ""
        if result:
            ocr_result = [line[1] for line in result]
            docs += "\n".join(ocr_result)
            print('jpg:\n',docs[:100])
        return docs


    #从file_path路径加载其下全部文件
    # for file in os.listdir(files_path):
    #     file_path = f'{files_path}/{file}'
    #     if file_path.endswith('.txt'):
    #         load_txt_file(file_path)
    #     elif file_path.endswith('.md'):
    #         load_md_file(file_path)
    #     elif file_path.endswith('.pdf'):
    #         load_pdf_file(file_path)
    #     elif file_path.endswith('.jpg'):
    #         load_jpg_file(file_path)


    # 不同格式文件的分割

    #分割txt文件
    def load_txt_splitter(self, txt_file, chunk_size=200, chunk_overlap=20):
        docs = self.load_txt_file(txt_file)
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = text_splitter.split_documents(docs)
        #默认展示分割后第一段内容
        print('split_docs[0]: ', split_docs[0])
        return split_docs

    #分割pdf文件
    def load_pdf_splitter(self, pdf_file, chunk_size=200, chunk_overlap=20):
        docs = self.load_pdf_file(pdf_file)
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = text_splitter.split_documents(docs)
        #默认展示分割后第一段内容
        print('split_docs[0]: ', split_docs[0])
        return split_docs

    #分割md文件
    def load_md_splitter(self, md_file, chunk_size=200, chunk_overlap=20):
        docs = self.load_md_file(md_file)
        text_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = text_splitter.split_documents(docs)
        #默认展示分割后第一段内容
        print('split_docs[0]: ', split_docs[0])
        return split_docs

    #分割jpg文件
    def load_jpg_splitter(self, jpg_file, chunk_size=200, chunk_overlap=20):
        docs = self.load_jpg_file(jpg_file)
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = text_splitter.create_documents([docs])
        #默认展示分割后第一段内容
        print('split_docs[0]: ', split_docs[0])
        return split_docs

    #将所有文件分割后得到的chunk合并至一个list
    def merge_chunks(self,chunks):
        merged_chunks = []
        for chunk in chunks:
            merged_chunks.extend(chunk)
        return merged_chunks

    #从file_path路径加载并分割其下全部文件
    def load_and_split_files(self, files_path, chunk_size=200, chunk_overlap=80):
        docs = []
        for file in os.listdir(files_path):
            # file_path = f'{files_path}/{file}'
            if file.lower().endswith('.txt'):
                docs.append(self.load_txt_splitter(file))
            elif file.lower().endswith('.md'):
                docs.append(self.load_md_splitter(file))
            elif file.lower().endswith('.pdf'):
                docs.append(self.load_pdf_splitter(file))
            elif file.lower().endswith('.jpg'):
                docs.append(self.load_jpg_splitter(file))
        merged_chunks = self.merge_chunks(docs)
        return merged_chunks
    
    #根据文件的相对路径加载并分割全部文件, file_rel_paths传入文件名（如test.txt）的数组
    def load_and_split_files_by_relpaths(self, file_rel_paths, chunk_size=200, chunk_overlap=80):
        docs = []
        for file in file_rel_paths:
            # file_path = f'{files_path}/{file}'
            if file.lower().endswith('.txt'):
                docs.append(self.load_txt_splitter(file))
            elif file.lower().endswith('.md'):
                docs.append(self.load_md_splitter(file))
            elif file.lower().endswith('.pdf'):
                docs.append(self.load_pdf_splitter(file))
            elif file.lower().endswith('.jpg'):
                docs.append(self.load_jpg_splitter(file))
        merged_chunks = self.merge_chunks(docs)
        return merged_chunks









