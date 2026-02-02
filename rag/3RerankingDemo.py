import os
import httpx

# embeding（参考EmbeddingDemo.py）
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
docs = [
    Document(page_content="苹果富含维生素C，有利于健康。", metadata={"id": 1, "topic": "fruit"}),
    Document(page_content="特斯拉是一家电动汽车公司。", metadata={"id": 2, "topic": "tech"}),
    Document(page_content="香蕉含有丰富的钾元素。", metadata={"id": 3, "topic": "fruit"}),
]
embeddings = OpenAIEmbeddings(model="Qwen/Qwen3-Embedding-8B", base_url="https://api.siliconflow.cn/v1", api_key="sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug")
vector_store = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="my_knowledge_base" # 集合名称
)
base_retriever = vector_store.as_retriever(search_kwargs={"k": 5}) # 初排取5个

# 2. 定义重排模型 (API)
model = "Qwen/Qwen3-Reranker-8B"
base_url = "https://api.siliconflow.cn/v1"
api_key = "sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug"

def rerank_with_api(query: str, docs, top_n: int = 2):
    if not api_key:
        raise RuntimeError("缺少 API Key，请设置 SILICONFLOW_API_KEY 或 OPENAI_API_KEY")

    payload = {
        "model": model,
        "query": query,
        "documents": [d.page_content for d in docs],
        "top_n": top_n,
    }

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/rerank"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    results = data.get("results") or data.get("data") or []
    # 兼容返回字段：index / relevance_score
    ranked = []
    for item in results:
        idx = item.get("index")
        score = item.get("relevance_score") or item.get("score")
        if idx is not None and 0 <= idx < len(docs):
            ranked.append((docs[idx], score))
    return ranked

# 3. 执行重排检索
query = "水果的营养成分"
initial_docs = base_retriever.invoke(query)
reranked = rerank_with_api(query, initial_docs, top_n=2)

print("--- 重排后结果(含得分) ---")
for doc, score in reranked:
    print(f"score: {score}")
    print(doc.page_content)