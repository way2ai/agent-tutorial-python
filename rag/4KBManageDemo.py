import uuid
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 1. 添加带有唯一 ID 的文档
doc_id_1 = str(uuid.uuid4())
doc_id_2 = str(uuid.uuid4())

new_docs = [
    Document(page_content="Python 3.12 发布了新特性。", metadata={"source": "news", "year": 2024}, id=doc_id_1),
    Document(page_content="旧的Python 2.7 已经停止维护。", metadata={"source": "history", "year": 2020}, id=doc_id_2)
]
embeddings = OpenAIEmbeddings(model="Qwen/Qwen3-Embedding-8B", base_url="https://api.siliconflow.cn/v1", api_key="sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug")
vector_store = Chroma.from_documents(
    documents=new_docs,
    embedding=embeddings,
    collection_name="my_knowledge_base" # 集合名称
)
base_retriever = vector_store.as_retriever(search_kwargs={"k": 5}) # 初排取5个

# add_documents 会返回 IDs
ids = vector_store.add_documents(new_docs, ids=[doc_id_1, doc_id_2])
print(f"已添加文档 ID: {ids}")

# 2. 元数据过滤检索 (Metadata Filtering)
# 只想找 2024 年的新闻
filter_retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 1,
        "filter": {"year": 2024} # 关键点：元数据过滤
    }
)
res = filter_retriever.invoke("Python")
print(f"过滤检索结果: {res[0].page_content}")

# 3. 删除文档 (基于 ID)
vector_store.delete(ids=[doc_id_2]) # 删除旧文档
print("已删除 Python 2.7 文档")

# 验证删除
res_check = vector_store.similarity_search("Python 2.7", k=1)
# 此时应该检索不到被删除的内容，或者检索到的是其他内容
print(f"删除后检索结果: {[doc.page_content for doc in res_check]}")