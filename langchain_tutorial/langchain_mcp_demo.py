from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

# 创建模型
from langchain_openai import ChatOpenAI
openai_model = ChatOpenAI(
    model="Qwen/Qwen3-14B",
    api_key="sk-xxx",
    base_url="https://api.siliconflow.cn/v1"
)

# 创建mcp-client
from langchain_mcp_adapters.client import MultiServerMCPClient 
client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp",
        }
    }
)

async def main():

    # 加载工具
    tools = await client.get_tools()  
    # 创建代理
    agent = create_agent(
        openai_model,
        tools,
        debug=False,
        name="Excel Agent",
    )

    # 调用工具
    try:
        print("开始调用工具...")
        payload = {"messages": [
                {"role": "system", "content": "你是一个乐于助人的助手，擅长使用提供的工具解决问题，回答要简洁明了。"},
                {"role": "user", "content": "创建一个测试excel"}
            ]}
        
        tasks = [
             agent.ainvoke(payload) for i in range(1, 10 + 1)
        ]
        results =  await asyncio.gather(*tasks, return_exceptions=True)
        print(results)
        # result = await agent.ainvoke(payload)
        # result2 = await agent.ainvoke(payload)
        # pretty_print_result(result)
        # print("\n\n--- 第二次调用 ---\n\n")
        # pretty_print_result(result2)
    except Exception as e:
        print(f"工具调用失败: {e}")

def pretty_print_result(result: dict) -> None:
    """友好展示 agent 返回结果。"""
    messages = result.get("messages", [])
    final_answer = None
    tool_steps: list[str] = []

    for msg in messages:
        msg_type = getattr(msg, "type", None) or msg.__class__.__name__
        if msg_type == "ai":
            content = getattr(msg, "content", None)
            if content:
                final_answer = content
        elif msg_type == "tool":
            tool_name = getattr(msg, "name", "tool")
            content = getattr(msg, "content", None)
            if isinstance(content, list):
                content_text = "\n".join(
                    item.get("text", "") for item in content if isinstance(item, dict)
                ).strip()
            else:
                content_text = str(content).strip() if content is not None else ""
            if content_text:
                tool_steps.append(f"[{tool_name}] {content_text}")

    print("\n===== 工具调用结果 =====")
    if tool_steps:
        for step in tool_steps:
            print(step)
    else:
        print("(无工具输出)")

    print("\n===== 最终回答 =====")
    print(final_answer or "(无最终回答)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())