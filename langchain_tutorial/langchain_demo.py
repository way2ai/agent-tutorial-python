from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

from langchain_openai import ChatOpenAI
openai_model = ChatOpenAI(
    model="Qwen/Qwen3-32B",
    api_key="sk-zhretbftokbdkvvyoshzxpvzkbvfrkumcuoqkopfswpwuhja",
    temperature=0.1,
    base_url="https://api.siliconflow.cn/v1"
)

from langchain_mcp_adapters.client import MultiServerMCPClient 
client = MultiServerMCPClient(  
    {
        "excel": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp",
        }
    }
)

async def main():

    system_prompt = "你是一个乐于助人的助手，擅长使用提供的工具解决问题，回答要简洁明了。"

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
        excel_response = await agent.ainvoke(
            {"messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "创建一个excel：文件名称为“test”，内容为[['name','age'],['Bob','20'],['张三','23']]"}
                ]}
        )
        print("工具调用结果:", excel_response)
    except Exception as e:
        print(f"工具调用失败: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())