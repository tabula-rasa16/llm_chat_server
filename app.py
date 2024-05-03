from typing import Optional

from fastapi import FastAPI, File, UploadFile

# 静态文件夹配置
from fastapi.staticfiles import StaticFiles

import datetime
from pathlib import Path

import pymysql

from utils import *
from common.jsontools import *

# 引入实体类
from entityModels import *

# from llm_initial.chatGLM2 import ChatGLM2


# 引入LangChain相关封装模块
# from langChain_model.fileLoader import FileLoader
# from langChain_model.knowledgeBase import KnowledgeBase
# from langChain_model.chat import Chat

# 引入llm
# from llm_initial.chatGLM2 import ChatGLM2

# 引入redis
import redis
import pickle

import base64


app = FastAPI(swagger_ui_parameters = {"syntaxHighlight.theme": "obsidian"})

# UPLOAD_FILE_PATH = r"D:\ChatGLM\llm_chat_server\test_files"
# upload_file_path = r".\static"
UPLOAD_FILE_PATH = r".\documents"

FAISS_DB_SAVE_PATH = "FaissDB"

# llm部署接口url
LLM_URL = "http://127.0.0.1:8000"

# 静态文件夹配置
# app.mount("/static", StaticFiles(directory="static"), name="static")

#数据库连接
# db = pymysql.connect(host='localhost', user='root', password='root', db='llm_chat', charset='utf8mb3') #本地
db = pymysql.connect(host='120.27.157.134', user='root', password='Z@[fl9>Y2Mg4z}wm0sD+MG2R4GULzOQsCy6;"6^t', db='llm_chat', charset='utf8mb4')
cursor = db.cursor()

cursor.execute("SELECT VERSION()")
 
# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()
 
print ("Database version : %s " % data)

# 创建Redis连接
# redis_item = redis.Redis(host='localhost', port=6379, db=0)
redis_item = redis.Redis(host='120.27.157.134', port=6379, db=0)



# 初始化配置 LLM   !!!!!被部署在8080端口
# llm = ChatGLM2(url = "http://127.0.0.1:8080",top_p=0.9, temperature=0, max_token=10000)

# 定义对话chain
conversation_chain = None

# 定义当前知识库
current_knowledge_db = None




@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

#用户上传文件
@app.post("/fileHandler/uploadFile")
async def upload_file(file: UploadedFile):
    # 处理文件上传逻辑
    try:
         # 对 base64 编码的字符串进行解码
        file_bytes = base64.b64decode(file.file_bytes.encode('utf-8'))
        # 获取文件扩展名
        file_ext = Path(file.file_name).suffix
        # 获取当前时间戳
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        # 构造新的文件名
        new_filename = f"{file.file_name.split('.')[0]}_{timestamp}{file_ext}"
        
        with open(f"{UPLOAD_FILE_PATH}\\{new_filename}", "wb") as f:
            # content = await file.read()
            # f.write(content)
            f.write(file_bytes)
    except OSError as e:
        return reponse(code=500, message=f"File upload failed: {e}")
    except Exception as e:
        return reponse(code=500, message=f"Unexpected error: {e}")
    
    result = {"file_path": f"{UPLOAD_FILE_PATH}\\{new_filename}",
              "file_name": new_filename}
    return reponse(code=200, message="文件上传成功", data=result)





    # # 读取文件内容
    # content = await file.read()
    # # 将文件保存到本地
    # # todo 路径的斜杠在linux和windows下是不同的，需要进行处理
    # try:
    #     with open(f"{UPLOAD_FILE_PATH}\{file.filename}", "wb") as f:
    #         f.write(content)
    # except OSError as e:
    #     return reponse(code = 500, message = f"File upload failed: {e}")
    #     # return ({"message": f"File upload failed: {e}", "code": 500})
    # except Exception as e:
    #     return reponse(code = 500, message = f"Unexpected error: {e}")
    # result = {"file_path": f"{UPLOAD_FILE_PATH}\{file.filename}"}
    # return reponse(code = 200, message = "文件上传成功", data = result)
    # return {"message": "File uploaded successfully", "code": 200}

#用户注册
@app.post("/user/signup")
async def signup(request: SysUser):
    user_info = request
    print(user_info)
    # user_name = request.userName
    # password = request.password
    # print(type(user_info.user_name), type(user_info.password))

    # 检查用户名是否已存在
    query = "SELECT * FROM sys_user WHERE user_name = %s"
    cursor.execute(query, (user_info.user_name,))
    data = cursor.fetchone()
    if data is not None:
        # return {"message": "Username already exists", "code": 400}
        return reponse(code = 500, message = "用户名已存在，请使用其他用户名")
    # 检查密码是否符合要求
    if user_info.password is None or user_info.password == "":
        # return {"message": "Password cannot be empty", "code": 400}
        return reponse(code = 500, message = "密码不能为空")
    # 生成用户主键、创建时间等信息
    user_info = pre_insert(user_info)
    print(user_info)
    # uuid = generate_id()
    # # print(type(uuid))
    # del_flag = 0
    try:
        # query = "INSERT INTO sys_user (user_id, user_name, password) VALUES (%d, %s, %s)"
        # cursor.execute(query, (uuid, user_name, password))
        query = "INSERT INTO sys_user (user_id, user_name, password, del_flag, create_time) VALUES (%(user_id)s, %(user_name)s, %(password)s, %(del_flag)s, %(create_time)s)"
        cursor.execute(query, {'user_id': user_info.id, 'user_name': user_info.user_name, 'password': user_info.password, 'del_flag': user_info.del_flag, 'create_time': user_info.create_time})
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"Database error: {e}")
        # return {"message": f"Database error: {e}", "code": 500}
    
    # 返回注册成功的信息
    return reponse(code = 200, message = "注册成功")


#用户登录
@app.post("/user/login")
async def login(request: SysUser):
    user_info = request
    # 检查用户名是否存在
    query = "SELECT * FROM sys_user WHERE user_name = %s"
    cursor.execute(query, (user_info.user_name,))
    data = cursor.fetchone()
    if data is None:
        return reponse(code = 500, message = "用户名不存在，请先注册")
    # 检查密码是否正确
    if data[2] != user_info.password:
        return reponse(code = 500, message = "密码错误，请重新输入")
    # todo生成token并存储
    # token = generate_token()
    # 返回登录成功的信息与用户信息
    result = {"user_id": data[0],"user_name": data[1]}
    return reponse(code = 200, message = "登录成功", data = result)

#用户创建知识库
@app.post("/knowledgeDB/create")
async def create_knowledge_db(request: KnowledgeDB_Create):
    knowledge_db_info = request
    # files_info = knowledge_db_info.file_list
    # 检查知识库名称是否已存在
    query = '''SELECT tuk.id FROM 
            t_user_knowledgedb tuk 
            LEFT JOIN t_knowledgedb tk ON tuk.knowledgeDB_id = tk.knowledgeDB_id 
            WHERE tuk.user_id = %(user_id)s
            AND tk.knowledgeDB_name = %(knowledgeDB_name)s
            AND tk.del_flag = 0'''
    cursor.execute(query, {'user_id': knowledge_db_info.user_id, 'knowledgeDB_name': knowledge_db_info.knowledgeDB_name})
    data = cursor.fetchone()
    if data is not None:
        return reponse(code = 500, message = "知识库名称已存在，请使用其他名称")
    # 生成知识库主键
    knowledge_db_info = pre_insert(knowledge_db_info)
    # 新建知识库
    try:
        query = "INSERT INTO t_knowledgedb (knowledgeDB_id, knowledgeDB_name, del_flag, create_time) VALUES (%(knowledgeDB_id)s, %(knowledgeDB_name)s, %(del_flag)s, %(create_time)s)"
        cursor.execute(query, {'knowledgeDB_id': knowledge_db_info.id, 'knowledgeDB_name': knowledge_db_info.knowledgeDB_name, 'del_flag': knowledge_db_info.del_flag, 'create_time': knowledge_db_info.create_time})
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"新建knowledgedb时出现错误: Database error: {e}")
    
    print("knowledgedb新建成功")
    # 创建用户与知识库的关系
    id = generate_id()
    try:
        query = "INSERT INTO t_user_knowledgedb (id, user_id, knowledgeDB_id, del_flag, create_time) VALUES (%(id)s, %(user_id)s, %(knowledgeDB_id)s, %(del_flag)s, %(create_time)s)"
        cursor.execute(query, {'id': id, 'user_id': knowledge_db_info.user_id, 'knowledgeDB_id': knowledge_db_info.id, 'del_flag': knowledge_db_info.del_flag, 'create_time': knowledge_db_info.create_time})
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"新建用户与knowledgedb的关系时出现错误: Database error: {e}")
    

    # 根据文件列表新建文件记录
    document_list = []
    for file_info in knowledge_db_info.file_list:
        if file_info.del_flag == 1:
            continue
        document = Document(path_url = file_info.document_name)
        # document.path_url = file_info

        # 格式为xxxx.txt
        document.document_name = file_info.document_name.split('\\')[-1] # windows下路径
        # document.document_name = file_info.split('/')[-1] # linux下路径

        document = pre_insert(document)
        print(document)
        document_list.append(document)

    # 批量插入文件记录
    insert_query = """
        INSERT INTO t_document (document_id, document_name, path_url, document_type, del_flag, create_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

    data_values = []
    for doc in document_list:
        data_values.append((
            doc.id,
            doc.document_name,
            doc.path_url,
            doc.document_type,
            doc.del_flag,
            doc.create_time
        ))
    try:
        cursor.executemany(insert_query, data_values)
        db.commit()  
    except pymysql.Error as e:
        db.rollback()  
        return reponse(code = 500, message = f"插入文件记录时出现错误: Database error: {e}")
    
    # 创建知识库与文件的关系
    knowledgeDB_document_list = []
    for doc in document_list:
        knowledgeDB_document = KnowledgeDB_Document(knowledgeDB_id = knowledge_db_info.id, document_id = doc.id)
        knowledgeDB_document = pre_insert(knowledgeDB_document)
        # knowledgeDB_document.knowledgeDB_id = knowledge_db_info.id
        # knowledgeDB_document.document_id = doc.id
        print(knowledgeDB_document)
        knowledgeDB_document_list.append(knowledgeDB_document)
    
    # 批量插入关系记录
    insert_query = """
        INSERT INTO t_knowledgedb_document (id, knowledgeDB_id, document_id, del_flag, create_time)
        VALUES (%s, %s, %s, %s, %s)
        """

    data_values = []
    for item in knowledgeDB_document_list:
        data_values.append((
            item.id,
            item.knowledgeDB_id,
            item.document_id,
            item.del_flag,
            item.create_time
        ))
    try:
        cursor.executemany(insert_query, data_values)
        db.commit()  
    except pymysql.Error as e:
        db.rollback()  
        return reponse(code = 500, message = f"插入知识库-文件关系记录时出现错误: Database error: {e}")
    
    # todo 加载并读取文件，对向量数据库进行初始化
    # try:
    #     file_loader = FileLoader(files_path = UPLOAD_FILE_PATH)
    #     docs = file_loader.load_and_split_files_by_relpaths(knowledge_db_info.file_list)

    #     knowledge_db = KnowledgeBase()
    #     knowledge_db = knowledge_db.db_init(docs = docs)

        # 指定存储路径和文件名
        # index_path = f"{FAISS_DB_SAVE_PATH}\{knowledge_db_info.id}"

        # 保存到指定路径
        # knowledge_db.db_save(save_directory = index_path)
    #     knowledge_db.db_save()
    # except Exception as e:
    #     return reponse(code = 500, message = f"初始化知识库向量数据库时出现错误: {e}")
    
    # 返回知识库创建成功的信息
    return reponse(code = 200, message = "新建知识库成功", data= {"knowledgeDB_id": knowledge_db_info.id})


# 根据用户id获取知识库列表
@app.post("/knowledgeDB/list")
async def get_knowledge_db_list(request: SysUser_VO):
    user_info = request
    # 查询用户与知识库的关系
    query = '''
        SELECT tk.* FROM t_user_knowledgedb tuk 
        LEFT JOIN t_knowledgedb tk ON tuk.knowledgeDB_id = tk.knowledgeDB_id AND tuk.del_flag = 0 
        WHERE tuk.user_id = %(user_id)s
        AND tk.del_flag = 0 
        '''
    try:
        cursor.execute(query, {'user_id': user_info.user_id})
        db_list = cursor.fetchall()
        temp = {}
        result = []
        if(db_list is not None):
            for db in db_list:
                temp = {
                    "knowledgeDB_id": db[0],
                    "knowledgeDB_name": db[1],
                    "description": db[2],
                    "del_flag": db[3],
                    "create_time": datetime_serializer(db[4]),
                    "create_by": db[5],
                    "update_time": datetime_serializer(db[6]),
                    "update_by": db[7],
                }
                result.append(temp.copy())
            print("result:", result)
            return reponse(code = 200, message = "获取知识库列表成功", data = result)
        else:   
            return reponse(code = 200, message = "您还未创建任何知识库，请先前往创建")
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"获取知识库列表时出现错误: Database error: {e}")


# 删除知识库
@app.post("/knowledgeDB/delete")
async def delete_knowledge_db(request: KnowledgeDB_VO):
    knowledge_db_info = request
    update_time = generate_time()
    # 将删除标志位置为1
    query1 = '''UPDATE t_knowledgedb SET del_flag = 1, update_time = %(update_time)s WHERE knowledgeDB_id = %(knowledgeDB_id)s'''
    query2 = '''UPDATE t_user_knowledgedb SET del_flag = 1, update_time = %(update_time)s WHERE knowledgeDB_id = %(knowledgeDB_id)s'''
    try:
        cursor.execute(query1, {'knowledgeDB_id': knowledge_db_info.knowledgeDB_id, 'update_time': update_time})
        cursor.execute(query2, {'knowledgeDB_id': knowledge_db_info.knowledgeDB_id, 'update_time': update_time})
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"删除知识库时出现错误: Database error: {e}")
    return reponse(code = 200, message = "删除知识库成功")



# 根据知识库id获取知识库包含的文件详情
@app.post("/knowledgeDB/document/list")
async def get_knowledge_db_document_list(request: KnowledgeDB_VO):
    knowledge_db_info = request
    # 查询知识库与文件的关系
    query = '''
        SELECT td.*, tkd.in_vectorDB FROM t_knowledgedb_document tkd 
        LEFT JOIN t_document td ON tkd.document_id = td.document_id AND tkd.del_flag = 0 
        WHERE tkd.knowledgeDB_id = %(knowledgeDB_id)s
        AND td.del_flag = 0 
        '''
    try:
        cursor.execute(query, {'knowledgeDB_id': knowledge_db_info.knowledgeDB_id})
        document_list = cursor.fetchall()
        temp = {}
        result = []
        if(document_list is not None):
            for doc in document_list:
                temp = {
                    "document_id": doc[0],
                    "document_name": doc[1],
                    "path_url": doc[2],
                    "document_type": doc[3],
                    "del_flag": doc[4],
                    "create_time": datetime_serializer(doc[5]),
                    "update_time": datetime_serializer(doc[6]),
                    "in_vectorDB": doc[7],
                }
                result.append(temp.copy())
            print("result:", result)
            return reponse(code = 200, message = "获取知识库包含的文件列表成功", data = result)
        else:   
            return reponse(code = 200, message = "该知识库下暂无文件")
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"获取知识库包含的文件列表时出现错误: Database error: {e}")
    
# 根据文件id删除知识库中的一个文件id
@app.post("/knowledgeDB/document/delete")
async def delete_knowledge_db_document(request: Document_VO):
    document_info = request
    update_time = generate_time()
    # 删除文件记录
    query = '''UPDATE t_document SET del_flag = 1, update_time = %(update_time)s  WHERE document_id = %(document_id)s'''
    try:
        cursor.execute(query, {'document_id': document_info.document_id, 'update_time': update_time})
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"删除知识库中的文件时出现错误: Database error: {e}")
    
    # 删除数据库-文件关联记录
    query = '''UPDATE t_knowledgedb_document SET del_flag = 1, update_time = %(update_time)s  WHERE document_id = %(document_id)s'''
    try:
        cursor.execute(query, {'document_id': document_info.document_id, 'update_time': update_time})
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"删除知识库-文件关联关系时出现错误: Database error: {e}")

    return reponse(code = 200, message = "删除知识库中的文件成功")

# 向知识库中添加一个文件
@app.post("/knowledgeDB/document/add")
async def add_knowledge_db_document(request: Document_Add):
    document_info = request
    document_info = pre_insert(document_info)

    # 格式为xxxx.txt
    document_info.document_name = document_info.path_url.split('\\')[-1] # windows下路径
    # document.document_name = file_info.split('/')[-1] # linux下路径

    # 插入文件记录
    query = '''INSERT INTO t_document (document_id, document_name, path_url, document_type, del_flag, create_time) 
        VALUES (%(document_id)s, %(document_name)s, %(path_url)s, %(document_type)s, %(del_flag)s, %(create_time)s)'''
    try:
        cursor.execute(query, {
            "document_id": document_info.id,
            "document_name": document_info.document_name,
            "path_url": document_info.path_url,
            "document_type": document_info.document_type,
            "del_flag": document_info.del_flag,
            "create_time": document_info.create_time
        })
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"插入文件记录时出现错误: Database error: {e}")
    
    # 插入数据库与文件关系记录
    db_document_info = KnowledgeDB_Document(knowledgeDB_id = document_info.knowledgeDB_id, document_id = document_info.id)
    db_document_info = pre_insert(db_document_info)
    query = '''INSERT INTO t_knowledgedb_document (id, knowledgeDB_id, document_id, del_flag, create_time)
        VALUES (%(id)s, %(knowledgeDB_id)s, %(document_id)s, %(del_flag)s, %(create_time)s)'''
    try:
        cursor.execute(query, {
            "id": db_document_info.id,
            "knowledgeDB_id": db_document_info.knowledgeDB_id,
            "document_id": db_document_info.document_id,
            "del_flag": db_document_info.del_flag,
            "create_time": db_document_info.create_time
        })
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"插入数据库与文件关系记录时出现错误: Database error: {e}")
    
    return reponse(code = 200, message = "向知识库中添加文件成功")

# 批量更新知识库文件
@app.post("/knowledgeDB/update")
def update_knowledge_db_document(request: KnowledgeDB_Update):
    knowledge_DB_id = request.knowledgeDB_id
    knowledge_DB_name = request.knowledgeDB_name
    document_info_list = request.file_list

    # 对比知识库与文件关联关系，更新关联关系
    # # 获取传回的所有文件id
    # document_id_list = []
    # for file_info in document_info_list:
    #     if file_info.document_id is not None:
    #         document_id_list.append(file_info.document_id)
    # # 删除库中不在传回文件id列表中的文件
    # query = '''UPDATE t_knowledgedb_document 
    #             SET del_flag = 1, update_time = %(update_time)s  
    #             WHERE knowledgeDB_id = %(knowledgeDB_id)s 
    #             AND document_id NOT IN %(document_id_list)s'''
    # try:
    #     cursor.execute(query, {
    #         "knowledgeDB_id": knowledge_DB_id,
    #         "document_id_list": tuple(document_id_list),
    #         "update_time": generate_time()
    #     })
    #     db.commit()
    # except pymysql.Error as e:
    #     db.rollback()
    #     return reponse(code = 500, message = f"删除知识库中不在传回文件id列表中的文件时出现错误: Database error: {e}")

    # 修改知识库状态
    query = '''UPDATE t_knowledgedb SET 
            knowledgeDB_name = %(knowledgeDB_name)s, update_time = %(update_time)s 
            WHERE knowledgeDB_id = %(knowledgeDB_id)s'''
    try:
        cursor.execute(query, {
            "knowledgeDB_id": knowledge_DB_id,
            "knowledgeDB_name": knowledge_DB_name,
            "update_time": generate_time()
        })
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"更新知识库状态时出现错误: Database error: {e}")

    
    # 修改传回文件id列表中的文件状态
    query = '''UPDATE t_knowledgedb_document
                SET in_vectorDB = %s, update_time = %s, del_flag = %s
                WHERE knowledgeDB_id = %s
                AND document_id = %s'''
    data_values = []
    for file_info in document_info_list:
        if file_info.document_id is not None:
            data_values.append((
                file_info.in_vectorDB,
                generate_time(),
                file_info.del_flag,
                knowledge_DB_id,
                file_info.document_id
            ))
    try:
        cursor.executemany(query, data_values)
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return reponse(code = 500, message = f"更新知识库中文件状态时出现错误: Database error: {e}")
    
    # 为所有新上传的文件添加记录和关联关系
    new_document_list = []
    for file_info in document_info_list:
        if file_info.document_id is None:
            document = Document(path_url = file_info.document_name)
            # document.path_url = file_info

            # 格式为xxxx.txt
            document.document_name = file_info.document_name.split('\\')[-1] # windows下路径
            # document.document_name = file_info.split('/')[-1] # linux下路径

            document = pre_insert(document)
            print(document)
            new_document_list.append(document)
            
    # 插入文件记录
    # 批量插入文件记录
    insert_query = """
        INSERT INTO t_document (document_id, document_name, path_url, document_type, del_flag, create_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

    data_values = []
    for doc in new_document_list:
        data_values.append((
            doc.id,
            doc.document_name,
            doc.path_url,
            doc.document_type,
            doc.del_flag,
            doc.create_time
        ))
    try:
        cursor.executemany(insert_query, data_values)
        db.commit()  
    except pymysql.Error as e:
        db.rollback()  
        return reponse(code = 500, message = f"插入文件记录时出现错误: Database error: {e}")
    
    # 插入数据库与文件关系记录
    knowledgeDB_document_list = []
    for doc in new_document_list:
        knowledgeDB_document = KnowledgeDB_Document(knowledgeDB_id = knowledge_DB_id, document_id = doc.id)
        knowledgeDB_document = pre_insert(knowledgeDB_document)
        # knowledgeDB_document.knowledgeDB_id = knowledge_db_info.id
        # knowledgeDB_document.document_id = doc.id
        print(knowledgeDB_document)
        knowledgeDB_document_list.append(knowledgeDB_document)
    
    # 批量插入关系记录
    insert_query = """
        INSERT INTO t_knowledgedb_document (id, knowledgeDB_id, document_id, del_flag, create_time)
        VALUES (%s, %s, %s, %s, %s)
        """

    data_values = []
    for item in knowledgeDB_document_list:
        data_values.append((
            item.id,
            item.knowledgeDB_id,
            item.document_id,
            item.del_flag,
            item.create_time
        ))
    try:
        cursor.executemany(insert_query, data_values)
        db.commit()  
    except pymysql.Error as e:
        db.rollback()  
        return reponse(code = 500, message = f"插入知识库-文件关系记录时出现错误: Database error: {e}")
    
    return reponse(code = 200, message = "更新知识库文件成功")
    





# 刷新向量数据库，在知识库更新提交后调用
@app.post("/vector_DB/refresh")
def refresh_knowledge_db(request: KnowledgeDB_VO):
    # 根据知识库id获取知识库中所有文件
    # 查询知识库与文件的关系
    query = '''
        SELECT td.* FROM t_knowledgedb_document tkd 
        LEFT JOIN t_document td ON tkd.document_id = td.document_id AND tkd.del_flag = 0 AND tkd.in_vectorDB = 1
        WHERE tkd.knowledgeDB_id = %(knowledgeDB_id)s
        AND td.del_flag = 0 
        '''
    try:
        cursor.execute(query, {'knowledgeDB_id': request.knowledgeDB_id})
        document_list = cursor.fetchall()
        docs_names = []
        if(document_list is not None):
            for doc in document_list:
                docs_names.append(doc[1]) # 获取文件名
    
        # 更新向量数据库
        file_loader = FileLoader()
        docs = file_loader.load_and_split_files_by_relpaths(file_rel_paths = docs_names)

        index_path = f"{FAISS_DB_SAVE_PATH}\{request.knowledgeDB_id}"
        vector_db = KnowledgeBase(save_directory = index_path)
        vector_db.db_init(docs = docs)
        vector_db.db_save()
    except Exception as e:
        return reponse(code = 500, message = f"更新向量数据库时出现错误: {e}")
    
    return reponse(code = 200, message = "更新向量数据库成功")

    


# @app.post("/ceshi/refresh_DB")
# def refresh_knowledge_db(request: KnowledgeDB_VO):
#     # 根据知识库id获取知识库中所有文件
#     # 查询知识库与文件的关系
#     query = '''
#         SELECT td.* FROM t_knowledgedb_document tkd 
#         LEFT JOIN t_document td ON tkd.document_id = td.document_id AND tkd.del_flag = 0 
#         WHERE tkd.knowledgeDB_id = %(knowledgeDB_id)s
#         AND td.del_flag = 0 
#         '''
#     cursor.execute(query, {'knowledgeDB_id': request.knowledgeDB_id})
#     document_list = cursor.fetchall()
#     result = []
#     if(document_list is not None):
#         for doc in document_list:
#             result.append(doc[1]) # 获取文件名
#     print("result:", result)


#     # 以下为redis测试
#     # 将更新后的chain对象存储到Redis
#     ceshi = pickle.dumps(result)
#     redis_item.set(f'ceshi:{request.knowledgeDB_id}', ceshi)

#     item_get_from_redis = redis_item.get(f'ceshi:{request.knowledgeDB_id}')

#     # 使用pickle.loads()反序列化
#     result = pickle.loads(item_get_from_redis)

#     print(item_get_from_redis)

#     return reponse(code = 200, message = "获取文件名列表成功", data = result)





# # 初始化向量数据库（用户选择当前使用的知识库后调用） redis版本
# @app.post("/knowledgeDB/init")
# async def init_knowledge_db(request: KnowledgeDB_VO):
#     # global current_knowledge_db
#     db_info = request
#     # 根据Id加载向量数据库
#     # 根据Id拼接文件路径
#     try:
#         index_path = f"{FAISS_DB_SAVE_PATH}\{db_info.knowledgeDB_id}"
#         knowledge_base = KnowledgeBase(save_directory = index_path)
#         knowledge_base.db_load()
#         # current_knowledge_db = knowledge_base.db
#         # db_bytes = pickle.dumps(current_knowledge_db)
#         db_bytes = pickle.dumps(knowledge_base)
#         redis_item.set(f'knowledge_base:{db_info.knowledgeDB_id}', db_bytes)
#     except Exception as e:
#         return reponse(code = 500, message = f"加载向量数据库时出现错误: {e}")
    
#     return reponse(code = 200, message = "初始化加载向量数据库成功")


# # 初始化向量数据库（用户选择当前使用的知识库后调用）全局变量版本
# @app.post("/knowledgeDB/init")
# async def init_knowledge_db(request: KnowledgeDB_VO):
#     global current_knowledge_db
#     db_info = request
#     # 根据Id加载向量数据库
#     # 根据Id拼接文件路径
#     try:
#         index_path = f"{FAISS_DB_SAVE_PATH}\{db_info.knowledgeDB_id}"
#         knowledge_base = KnowledgeBase(save_directory = index_path)
#         knowledge_base.db_load()
#         current_knowledge_db = knowledge_base
        
#     except Exception as e:
#         return reponse(code = 500, message = f"加载向量数据库时出现错误: {e}")
    
#     return reponse(code = 200, message = "初始化加载向量数据库成功")





# 传入用户问句生成回答 redis版本
@app.post("/chat/answer")
async def get_answer(request: Chat_VO):
    # global conversation_chain
    query_info = request
    prompt = query_info.query

    print("prompt:", prompt)
    
    response = ""

    try:
        # 从Redis中获取chain对象
        chain_bytes = redis_item.get(f'chain:{query_info.session_id}')

        if chain_bytes:
            chain = pickle.loads(chain_bytes)
        else:
            # 首次问答，需要获取向量数据库
            current_knowledge_db_bytes = redis_item.get(f'knowledge_base:{query_info.knowledgeDB_id}')
            # 需要反序列化
            current_knowledge_db = pickle.loads(current_knowledge_db_bytes)

            # 进行相似向量检索
            topK_docs = current_knowledge_db.similar_vectors_search(prompt, k = 3)

            # 第一次问答，先初始化对话链
            chat = Chat(llm=llm)
            # chat = Chat(llm=llm, max_history = query_info.max_history)
            # memory = ConversationBufferWindowMemory(k=5)
            # chain = RetrievalQAWithSourcesChain(llm=llm, memory=memory)
            chain = chat.chain
            # 构造prompt
            prompt = chat.prompt_create(topK_docs = topK_docs, query = query_info.query)



        # 使用chain处理问题
        response = chain.run(prompt)

        # 将更新后的chain对象存储到Redis
        chain_bytes = pickle.dumps(chain)
        redis_item.set(f'chain:{query_info.session_id}', chain_bytes)
    except Exception as e:
        return reponse(code = 500, message = f"生成回答时出现错误: {e}")
    
    return reponse(code = 200, message = "生成回答成功", data = response)



# 传入用户问句生成回答 全局变量版本
@app.post("/chat/answer")
async def get_answer(request: Chat_VO):
    global current_knowledge_db
    query_info = request
    prompt = query_info.query

    print("prompt:", prompt)
    
    response = ""

    try:
        # 从Redis中获取chain对象
        chain_bytes = redis_item.get(f'chain:{query_info.session_id}')

        if chain_bytes:
            chain = pickle.loads(chain_bytes)
        else:
            # # 首次问答，需要获取向量数据库
            # current_knowledge_db_bytes = redis_item.get(f'knowledge_base:{query_info.knowledgeDB_id}')
            # # 需要反序列化
            # current_knowledge_db = pickle.loads(current_knowledge_db_bytes)

            # 进行相似向量检索
            topK_docs = current_knowledge_db.similar_vectors_search(prompt, k = 3)

            # 第一次问答，先初始化对话链
            # chat = Chat(llm=llm, max_history = query_info.max_history)
            chat = Chat(llm=llm)
            # memory = ConversationBufferWindowMemory(k=5)
            # chain = RetrievalQAWithSourcesChain(llm=llm, memory=memory)
            chain = chat.chain
            # 构造prompt
            prompt = chat.prompt_create(topK_docs = topK_docs, query = query_info.query)



        # 使用chain处理问题
        response = chain.run(prompt)

        # 将更新后的chain对象存储到Redis
        chain_bytes = pickle.dumps(chain)
        redis_item.set(f'chain:{query_info.session_id}', chain_bytes)
    except Exception as e:
        return reponse(code = 500, message = f"生成回答时出现错误: {e}")
    
    return reponse(code = 200, message = "生成回答成功", data = response)

    












# 更新大模型参数配置
# def update_llm(request: LLM_VO):
#     llm_info = request
#     llm = ChatGLM2(url = LLM_URL, top_p = llm_info.top_p, temperature = llm_info.temperature, max_token = llm_info.max_token)
#     return llm







        



    

