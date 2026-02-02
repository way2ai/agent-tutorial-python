from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 模拟长文档
long_text = """
RAG技术架构详解。
RAG主要包含三个部分：索引、检索和生成。
在索引阶段，我们需要对文档进行切分。
切分的粒度直接影响检索的质量。
如果切分太细，可能丢失上下文；如果太粗，包含太多无关信息。
"""

# 2. 初始化切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=50,       # 每个块的大致字符数
    chunk_overlap=10,    # 块与块之间的重叠（保持上下文连贯性）
    separators=["\n", "。", "！", "，"] # 优先按这些符号切分
)

# 3. 执行切分
docs = text_splitter.create_documents([long_text])

print(f"切分后文档数量: {len(docs)}")
for i, doc in enumerate(docs):
    print(f"Chunk {i}:\n{doc.page_content}")