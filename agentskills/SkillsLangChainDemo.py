from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# --- 1. 定义技能 (Skills) ---
@tool
def calculate_length(text: str) -> int:
    """计算文本长度的技能。"""
    return len(text)

@tool
def get_weather(city: str) -> str:
    """查询天气的技能。"""
    return f"{city} 天气晴朗，25度"

# 这是一个技能列表 (Skill Set)
my_skills = [calculate_length, get_weather]

# --- 2. 装备技能给 Agent ---
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 使用 bind_tools 将技能“挂载”到模型上
llm_with_skills = llm.bind_tools(my_skills)

# --- 3. 调用 ---
query = "帮我看看北京天气怎么样，然后计算一下'北京'这两个字有多长？"
result = llm_with_skills.invoke(query)

# LangChain 会自动识别出需要调用两个技能
print(result.tool_calls) 
# 输出: [{'name': 'get_weather', 'args': {'city': '北京'}, ...}, {'name': 'calculate_length', ...}]