import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain.agents import create_agent

# 替换为你的实际 API Key
os.environ["SILICONFLOW_API_KEY"] = "sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug"

# 1. 定义工具 (Tools)
@tool
def add(a: int, b: int) -> int:
    """当需要计算两个数字相加时使用这个工具。"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """当需要计算两个数字相乘时使用这个工具。"""
    return a * b

tools = [add, multiply]

# 2. 定义模型 (LLM)
api_key = os.environ.get("SILICONFLOW_API_KEY")
if not api_key:
    raise RuntimeError("请在环境变量 SILICONFLOW_API_KEY 中配置 API key")

llm = ChatOpenAI(
    model="Qwen/Qwen3-32B",
    base_url="https://api.siliconflow.cn/v1",
    api_key=api_key,
)

# 3. 构建 Agent（LangChain 1.x 使用 create_agent）
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个乐于助人的数学助手。",
)

# 4. 运行
print("--- 简易智能体开始运行 ---")
inputs = {"messages": [HumanMessage(content="3乘以4再加上5等于多少？")]}
result = agent.invoke(inputs)
final_message = result["messages"][-1]
print(f"最终结果: {final_message.content}")