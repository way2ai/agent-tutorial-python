import operator
import os
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from pathlib import Path

# 建议使用环境变量传入 API Key，避免硬编码泄露
os.environ["SILICONFLOW_API_KEY"] = "sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug"

# 1. 定义状态 (State)
class State(TypedDict):
    topic: str
    draft: str
    arcticle: str
    final_article: str

llm = ChatOpenAI(
    model="Qwen/Qwen3-32B",
    base_url="https://api.siliconflow.cn/v1",
    api_key=os.environ.get("SILICONFLOW_API_KEY")
)

# 2. 定义节点 (Nodes) - 也就是工作流中的步骤
def write_draft(state: State):
    """步骤1：写初稿"""
    print("--- 正在写初稿 ---")
    msg = [
        SystemMessage(content="你是一个专业的作家。"),
        HumanMessage(content=f"请写一篇关于 {state['topic']} 的短文，100字以内。")
    ]
    response = llm.invoke(msg)
    return {"draft": response.content}

def polish_article(state: State):
    """步骤2：润色文章"""
    print("--- 正在润色文章 ---")
    msg = [
        SystemMessage(content="你是一个严格的编辑。"),
        HumanMessage(content=f"请优化这篇草稿，使其更生动：\n\n{state['draft']}")
    ]
    response = llm.invoke(msg)
    return {"arcticle": response.content}

def rm_ai(state: State):
    """步骤3：去除AI痕迹（可选）"""
    print("--- 正在去除AI痕迹 ---")
    msg = [
        SystemMessage(content="你是一个语言专家。"),
        HumanMessage(content=f"请修改以下内容，使其看起来不像AI生成的：\n\n{state['arcticle']}")
    ]
    response = llm.invoke(msg)
    return {"final_article": response.content}

# 3. 构建图 (Graph)
workflow = StateGraph(State)

# 添加节点
workflow.add_node("writer", write_draft)
workflow.add_node("editor", polish_article)
workflow.add_node("rm_ai", rm_ai)

# 定义边 (连接节点的逻辑)
workflow.set_entry_point("writer") # 从 writer 开始
workflow.add_edge("writer", "editor") # writer 之后去 editor
workflow.add_edge("editor", "rm_ai") # editor 之后去 rm_ai

workflow.add_edge("rm_ai", END) # rm_ai 之后结束

# 编译图
app = workflow.compile()

# 4. 运行
print("--- 工作流编排开始 ---")
print("流程: Start -> writer -> editor -> END")
print("Mermaid:\nflowchart LR\n  Start((Start)) --> writer[writer: 写初稿]\n  writer --> editor[editor: 润色文章]\n  editor --> End((End))\n")
inputs = {"topic": "人工智能的未来"}
result = app.invoke(inputs)
print(f"\n[最终产出]:\n{result['final_article']}")