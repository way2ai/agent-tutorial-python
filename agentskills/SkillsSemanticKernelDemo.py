import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

kernel = sk.Kernel()

# --- 1. 定义一个“软技能” (Semantic Function) ---
# 这个技能纯粹是用 Prompt 实现的，但被封装得像函数一样
joke_prompt = "给我讲一个关于 {{$topic}} 的简短笑话。"
joke_function = kernel.create_semantic_function(
    prompt_template=joke_prompt,
    function_name="TellJoke",
    skill_name="FunSkill", # 归类到“娱乐技能”包
    description="讲笑话"
)

# --- 2. 定义一个“硬技能” (Native Function) ---
# 这是一个真实的 Python 类
class MathSkill:
    @sk.skill_function(
        description="计算两个数字的和",
        name="Add"
    )
    def add(self, a: str, b: str) -> str:
        return str(float(a) + float(b))

# 导入硬技能
kernel.import_skill(MathSkill(), skill_name="MathSkill")

# --- 3. Agent 混合调用 ---
# 此时，Agent 的脑子里有两个技能包：FunSkill 和 MathSkill
# 它可以先计算，再讲笑话，或者混合使用。