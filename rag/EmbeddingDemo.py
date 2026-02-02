import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 假设已有切分好的文档
docs = [
    Document(page_content="苹果富含维生素C，有利于健康。", metadata={"id": 1, "topic": "fruit"}),
    Document(page_content="特斯拉是一家电动汽车公司。", metadata={"id": 2, "topic": "tech"}),
    Document(page_content="香蕉含有丰富的钾元素。", metadata={"id": 3, "topic": "fruit"}),
]

# 1. 初始化 Embedding 模型 (需要设置 OPENAI_API_KEY)
# os.environ["OPENAI_API_KEY"] = "sk-..."
embeddings = OpenAIEmbeddings(model="Qwen/Qwen3-Embedding-8B", base_url="https://api.siliconflow.cn/v1", api_key="sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug")

# 2. 构建向量库 (自动将文本转向量并存入)
vector_store = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="my_knowledge_base" # 集合名称
)

# 3. 检索 (Retrieval)
query = "哪些水果有营养？"
results = vector_store.similarity_search_with_relevance_scores(query, k=2)

print("--- 检索结果(含得分) ---")
for doc, score in results:
    print(f"score: {score}")
    print(doc.page_content)
    print(doc.metadata)