import json
from openai import OpenAI

client = OpenAI(api_key="sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug", base_url="https://api.siliconflow.cn/v1")

# --- 1. 模拟工具函数 ---
def get_weather(city):
    """模拟查询天气，返回不同城市的假数据"""
    print(f" >>> [系统正在查询] {city} 的天气...")
    if "北京" in city:
        return json.dumps({"city": "北京", "temp": 10}) # 北京冷一点
    elif "上海" in city:
        return json.dumps({"city": "上海", "temp": 20}) # 上海热一点
    else:
        return json.dumps({"city": city, "temp": 15})

# --- 2. 定义工具 Schema ---
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取城市气温",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"}
            },
            "required": ["city"]
        }
    }
}]

# --- 3. 能够处理多次调用的 Agent 循环 ---
def run_conversation():
    messages = [{"role": "user", "content": "比较一下北京和上海现在的气温，告诉我哪里更热？"}]
    
    print("--- 开始对话 ---")
    
    while True:
        # 发送请求给模型
        response = client.chat.completions.create(
            model="Qwen/Qwen3-32B",
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message
        
        # 情况A: 模型想调用工具 (可能是多个)
        if msg.tool_calls:
            messages.append(msg) # 必须先把模型想调用的意图加入历史
            
            print(f"\n--- 模型请求调用工具 ---:{msg.tool_calls}")
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"🤖 模型决定调用: {func_name} 参数: {args}")
                
                if func_name == "get_weather":
                    result = get_weather(args["city"])
                    
                    # 把结果封装成 message
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id, # 必须对应 ID
                        "content": result
                    })
            # 循环继续，把结果发回给模型，看它还需要什么
            
        # 情况B: 模型不再调用工具，直接回复文本
        else:
            print(f"\n✅ 最终回复: {msg.content}")
            break

run_conversation()