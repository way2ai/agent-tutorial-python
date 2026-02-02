"""
将步骤串联起来，构建一个问答链
"""
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 0. 准备向量库
docs = [
    Document(page_content="苹果富含维生素C，有利于健康。", metadata={"id": 1, "topic": "fruit"}),
    Document(page_content="特斯拉是一家电动汽车公司。", metadata={"id": 2, "topic": "tech"}),
    Document(page_content="香蕉含有丰富的钾元素。", metadata={"id": 3, "topic": "fruit"}),
]

embeddings = OpenAIEmbeddings(
    model="Qwen/Qwen3-Embedding-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug"
)

vector_store = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="my_knowledge_base",
)

compression_retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 1. 准备 LLM
llm = ChatOpenAI(
    model="Qwen/Qwen3-32B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug",
)

# 2. 定义 Prompt 模板
template = """
请基于以下上下文回答问题。如果你不知道，就说不知道，不要编造。

上下文：
{context}

问题：
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 3. 定义格式化函数 (将检索到的 docs 拼成字符串)
def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

# 4. 构建 LCEL (LangChain Expression Language) 链
# 流程：问题 -> 检索(带重排) -> 格式化文档 -> 填入Prompt -> LLM -> 解析输出
rag_chain = (
    {"context": compression_retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. 运行
response = rag_chain.invoke("香蕉含有什么元素？")
print(f"LLM 回答: {response}")