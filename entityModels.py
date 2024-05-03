# 用于定义实体类

from pydantic import BaseModel
from typing import Optional, List

class SysUser(BaseModel):
    id: Optional[int] = None
    user_name: str
    password: str
    del_flag: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None

class SysUser_VO(BaseModel):
    user_id: int

class UploadedFile(BaseModel):
    file_name: str
    file_bytes: str

class KnowledgeDB(BaseModel):
    id: Optional[int] = None
    knowledgeDB_name: str
    description: Optional[str] = None
    del_flag: Optional[str] = None  
    create_time: Optional[str] = None
    update_time: Optional[str] = None

class KnowledgeDB_VO(BaseModel):
    knowledgeDB_id: int


class FileInfo(BaseModel):
    document_id: Optional[int] = None
    document_name: str
    del_flag: Optional[str] = None
    in_vectorDB: Optional[str] = None


# 用于接收新建数据库的实体
class KnowledgeDB_Create(KnowledgeDB):
    user_id: int
    file_list: List[FileInfo] = [] #文件列表



# 用于接收更新知识库的实体
class KnowledgeDB_Update(BaseModel):
    knowledgeDB_id: int
    knowledgeDB_name: Optional[str] = None
    file_list: List[FileInfo] = [] #文件列表


class Document(BaseModel):
    id: Optional[int] = None
    document_name: Optional[str] = None
    path_url: str
    document_type: Optional[str] = None
    del_flag: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None

class Document_VO(BaseModel):
    document_id: int

class Document_Add(Document):
    knowledgeDB_id: int

class KnowledgeDB_Document(BaseModel):
    id: Optional[int] = None
    knowledgeDB_id: int
    document_id: int
    del_flag: Optional[str] = None
    in_vectorDB: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None


class LLM_VO(BaseModel):
    max_token: Optional[int] = None # 定义 max_token 属性
    temperature: Optional[float] = None # 定义 temperature 属性 
    top_p: Optional[float] = None # 定义 top_p 属性

class Chat_VO(BaseModel):
    query: str
    max_history : Optional[int] = None
    session_id: str
    knowledgeDB_id: int

