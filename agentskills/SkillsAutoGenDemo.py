"""
Docstring for agentskills.SkillsAutogenDemo

AutoGen (微软的另一个多 Agent 框架)
AutoGen 更强调 Agent 之间的对话。在这个框架里，Skill 是通过 register_function 注册给特定的 Agent（比如 UserProxyAgent 或 AssistantAgent）的。
特点：AutoGen 的 Skills 带有**“权限”**属性——谁能调用（Caller），谁来执行（Executor）。
"""
from autogen import AssistantAgent, UserProxyAgent, register_function

# --- 1. 定义技能函数 ---
def calculator(a: int, b: int) -> int:
    return a + b

def currency_converter(amount: float, from_currency: str, to_currency: str) -> float:
    return amount * 7.2  # 假装汇率是 7.2

# --- 2. 创建 Agents ---
# 助理 Agent (大脑)
assistant = AssistantAgent(
    name="assistant",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "xxx"}]}
)

# 用户代理 Agent (执行者/人类替身)
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config=False, # 关闭默认的代码执行，只用我们注册的函数
)

# --- 3. 注册技能 (技能绑定) ---
# 将 calculator 和 currency_converter 注册给这两个 Agent
# 这样它们在对话时就可以使用这些技能了
register_function(
    calculator,
    caller=assistant,  # 只有助理能决定"我要调用这个"
    executor=user_proxy, # 只有用户代理能真正"执行这个函数"
    name="calculator",
    description="一个简单的加法计算器"
)

# --- 4. 开始任务 ---
user_proxy.initiate_chat(
    assistant,
    message="计算 5 加 3 等于多少？"
)