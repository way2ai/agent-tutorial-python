import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent 
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage # 引入消息类型以便判断

async def run_mcp_demo():
    # 1. 定义 MCP 连接
    client = MultiServerMCPClient(
        {
            "mcp-excel": {
                "transport": "sse",
                "url": "http://localhost:8000/sse",
            }
        }
    )

    print("🚀 正在连接 MCP 服务...")

    try:
        tools = await client.get_tools()
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    if not tools:
        print("⚠️ 警告: 未找到任何工具")
        return
    
    print(f"🛠️ 成功加载工具 ({len(tools)}个): {[t.name for t in tools]}")

    # 2. 初始化模型
    llm = ChatOpenAI(
        # 注意：目前通用名称通常是 Qwen/Qwen2.5-32B-Instruct
        # 如果你确定有 Qwen3 权限则保持不变，否则建议改回 Qwen2.5
        model="Qwen/Qwen2.5-32B-Instruct", 
        openai_api_key="sk-zhretbftokbdkvvyoshzxpvzkbvfrkumcuoqkopfswpwuhja",
        # 硅基流动国内节点地址
        openai_api_base="https://api.siliconflow.cn/v1",
        temperature=0
    )

    # 3. 创建 Agent
    agent = create_react_agent(llm, tools)

    # 4. 提问
    query = "调用create_excel_file工具：参数名称为“test”，内容为[['name','age'],['Bob','20'],['张三','23']]"
    print(f"\n👤 用户提问: {query}")
    print("-" * 50)

    # 【核心修改】使用 astream 代替 ainvoke，实时获取中间步骤
    try:
        # stream_mode="values" 会返回状态的完整更新，这里我们默认遍历事件
        async for chunk in agent.astream({"messages": [HumanMessage(content=query)]}):
            
            # chunk 的格式通常是: {'agent': {'messages': [...]}} 或 {'tools': {'messages': [...]}}
            for node_name, node_content in chunk.items():
                
                # 获取该节点产生的新消息
                if "messages" in node_content:
                    for msg in node_content["messages"]:
                        
                        # 情况 A: 模型决定调用工具 (AIMessage 且包含 tool_calls)
                        if isinstance(msg, AIMessage) and msg.tool_calls:
                            print(f"\n🧠 [模型思考] 决定调用工具:")
                            for tool_call in msg.tool_calls:
                                print(f"   └─ 工具名称: {tool_call['name']}")
                                print(f"   └─ 参数内容: {tool_call['args']}")
                        
                        # 情况 B: 工具执行完毕返回结果 (ToolMessage)
                        elif isinstance(msg, ToolMessage):
                            print(f"\n🔧 [工具结果] (ID: {msg.tool_call_id}):")
                            print(f"   └─ 返回值: {msg.content}")

                        # 情况 C: 模型最终回复 (AIMessage 且没有 tool_calls)
                        elif isinstance(msg, AIMessage) and not msg.tool_calls:
                            print(f"\n💡 [最终回答]:\n{msg.content}")

    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    asyncio.run(run_mcp_demo())