import re,random
from openai import OpenAI

client = OpenAI(api_key="sk-zsajewmdqohlpuoahgkqbvrjjgzoewatgioabipfbiwscoug", base_url="https://api.siliconflow.cn/v1")

# --- 1. 定义实际函数 ---
def get_weather(city):
    print(f"   >>> [工具执行] 正在查询 {city}...")
    if "北京" in city: return "北京气温是10度"
    if "上海" in city: return "上海气温是20度"
    return "未知"

# --- 2. 构建 ReAct 专用的 System Prompt ---
# 这里必须教会模型如何思考、如何输出特定格式
REACT_PROMPT = """
尽你所能回答用户问题。你可以使用以下工具：

get_weather: 用于查询天气，输入参数为城市名。

请严格遵循以下格式：

Question: 需要回答的问题
Thought: 你应该思考下一步做什么
Action: [get_weather] 中的一个
Action Input: 具体的参数
Observation: 工具返回的结果
... (Thought/Action/Observation 可以重复多次)
Final Answer: 对原始问题的最终回答

开始！
"""

# --- 3. 循环执行 (ReAct Loop) ---
def react_agent(question):
    history = REACT_PROMPT + f"\nQuestion: {question}\n"
    
    for i in range(5): # 最多循环5次，防止死循环
        # 发送请求
        response = client.chat.completions.create(
            model="Qwen/Qwen3-32B",
            messages=[{"role": "user", "content": history}],
            stop=["Observation:"] # 关键：告诉模型生成到 Observation 之前停下，等我填结果
        )
        
        content = response.choices[0].message.content
        print(f"--- 第 {i+1} 步思考 ---\n{content}")
        history += content # 把模型的思考拼接到历史里
        
        # --- 4. 痛苦的文本解析环节 ---
        # 如果模型输出了 "Final Answer"，说明结束了
        if "Final Answer:" in content:
            return content.split("Final Answer:")[1].strip()
        
        # 解析 Action 和 Action Input (这里最容易出错！)
        # 假设模型输出：Action: get_weather \n Action Input: 北京
        action_match = re.search(r"Action:\s*(.*?)\n", content)
        input_match = re.search(r"Action Input:\s*(.*)", content)
        
        if action_match and input_match:
            action = action_match.group(1).strip()
            action_input = input_match.group(1).strip()
            
            # 执行工具
            if action == "get_weather":
                observation = get_weather(action_input)
                
                # 拼接 Observation 到历史，准备下一轮
                obs_str = f"\nObservation: {observation}\n"
                history += obs_str
                print(f"--- 工具返回 ---\n{obs_str}")
            
        else:
            print(f"解析失败，模型格式错了...{content}")
            # 手动提示它
            history += "\nObservation: 格式错误，请严格按照 Action 和 Action Input 格式。\n"

# 运行
result = react_agent("比较一下北京和上海现在的气温，告诉我哪里更热？")
print(f"\n最终结果: {result}")