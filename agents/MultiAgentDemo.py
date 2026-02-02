
import os
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
import operator

# 请通过环境变量传入 API Key，避免硬编码泄露
os.environ["SILICONFLOW_API_KEY"] = "sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug"



# --- 简单的模拟工具 ---
@tool
def web_search(query: str):
    """搜索互联网信息"""
    return f"搜索结果：关于 {query} 的最新数据是 2024年增长了50%。"

@tool
def generate_chart(data: str):
    """根据数据生成图表代码"""
    return f"生成了图表代码，数据来源：{data}"

# --- 1. 定义多智能体的状态 ---
# messages 列表会随着不同 agent 的发言而不断增长
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    next: str # 记录下一个该谁行动

llm = ChatOpenAI(
    model="Qwen/Qwen3-32B",
    base_url="https://api.siliconflow.cn/v1",
    api_key=os.environ.get("SILICONFLOW_API_KEY")
)
# --- 2. 定义各个 Agent 的节点 ---

def researcher_node(state: AgentState):
    print("--> 研究员正在工作...")
    # 这里简化处理，直接调用工具或模拟回复
    # 实际场景中，这里会是一个完整的 AgentExecutor
    last_message = state["messages"][-1]
    result = web_search.invoke(last_message.content)
    return {"messages": [HumanMessage(content=f"研究员结果: {result}", name="Researcher")]}

def charter_node(state: AgentState):
    print("--> 制图员正在工作...")
    last_message = state["messages"][-1]
    result = generate_chart.invoke(last_message.content)
    return {"messages": [HumanMessage(content=f"制图员结果: {result}", name="Charter")]}

# --- 3. 定义主管 (Supervisor) ---
# 主管是一个 LLM 链，它根据历史对话决定下一步是谁，或者结束
system_prompt = (
    "你是一个主管。你有两个工人：Researcher 和 Charter。"
    "根据用户的请求，决定下一步让谁行动。"
    "如果需要查资料，选 Researcher。"
    "如果有了数据需要画图，选 Charter。"
    "如果任务完成了，回复 FINISH。"
)

def supervisor_node(state: AgentState):
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    # 强制 LLM 输出下一步的名称（需要完整 JSON Schema）
    next_schema = {
        "type": "object",
        "title": "NextAgent",
        "description": "Supervisor decides which agent goes next",
        "properties": {
            "next_agent": {
                "type": "string",
                "enum": ["Researcher", "Charter", "FINISH"],
                "description": "Which agent should act next or FINISH",
            }
        },
        "required": ["next_agent"],
    }
    response = llm.with_structured_output(next_schema, strict=False).invoke(messages)
    
    next_agent = response["next_agent"]
    print(f"--- 主管决定下一步: {next_agent} ---")
    return {"next": next_agent}

# --- 4. 构建图 ---
workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Charter", charter_node)

workflow.set_entry_point("Supervisor")

# 添加条件边：Supervisor 决定去哪里
workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next"], # 读取 state['next'] 的值
    {
        "Researcher": "Researcher",
        "Charter": "Charter",
        "FINISH": END
    }
)

# 工人做完事后，回到 Supervisor 汇报
workflow.add_edge("Researcher", "Supervisor")
workflow.add_edge("Charter", "Supervisor")

app = workflow.compile()

# --- 5. 运行 ---
print("--- 多智能体协作开始 ---")
inputs = {
    "messages": [HumanMessage(content="请帮我查一下2024年的数据，然后根据结果画个图。")]
}
for s in app.stream(inputs):
    pass # stream 用于流式输出，这里仅为了执行