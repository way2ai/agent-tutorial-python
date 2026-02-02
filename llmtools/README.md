## ReAct 和 Function Calling

ReAct 和 Function Calling 都是让大模型（LLM）具备“使用工具能力”（Agent）的核心技术，但它们处于技术发展的不同阶段。
简单来说：ReAct 是“软实现”（通过提示词工程），Function Calling 是“硬实现”（通过模型微调和底层架构）

### Function Calling（函数调用）

### ReAct Reason + Act（推理 + 行动）。
含义：这是在大模型原生支持 Function Calling 之前最经典的 Agent 模式。它要求模型遵循一个固定的思维链模式：
1. Thought（思考）：我现在需要做什么？
2. Action（行动）：我决定调用搜索工具，参数是XXX。
3. Observation（观察）：工具返回了结果YYY。
4. Thought（再思考）：根据结果，我应该怎么回答用户？

### 联系
目标一致：两者的终极目标都是为了解决大模型无法联网、无法精确计算、无法操作外部系统的问题。它们都是为了连接 LLM（大脑） 和 Tools（手脚）。
演进关系：ReAct 是早期的通用解决方案（2022年提出）；Function Calling 是 OpenAI 在 2023 年推出的优化方案，随后被 DeepSeek、Qwen 等模型跟进。

### 区别
|特性|	ReAct(Reason + Act)|	Function Calling (函数调用)|
|--|--|--|
|实现原理|	提示词工程 (Prompt Engineering)|	模型原生微调|(Fine-tuning)|
|输出格式|	非结构化文本（包含思考、行动关键字）|	结构化数据（通常是 JSON）|
|解析方式|	需要用正则 (Regex) 从文本中提取参数|	直接解析 JSON 对象|
|思考过程|	显式输出（Thought: ...）|	隐式（通常直接给结果），或仅在内部思考|
|稳定性|	较低（模型容易废话或格式错误）|	极高（由模型底层强约束）|
|Token消耗|	高（因为要输出大量的思考文本）|	低（直奔主题）|

### 技术实现
1. ReAct
    实现逻辑是强依赖于一个精心设计的 System Prompt（系统提示词）。

步骤 1：构建 Prompt
开发者会在后台把 Prompt 构造成这样发给模型：
~~~text
System: 你是一个智能助手。你可以使用以下工具：
1. get_weather(city_name): 查询天气。

请遵循以下格式回答：
Question: 用户的问题
Thought: 我应该做什么...
Action: 工具名称
Action Input: 工具参数
Observation: 工具返回的结果
...（重复直到得出结论）
Final Answer: 最终给用户的回复

User: 查询一下北京现在的天气。
~~~

步骤 2：模型推理与正则提取
模型会按照这个格式“续写”文本：
~~~text
Thought: 用户想查天气，我需要用 get_weather 工具。
Action: get_weather
Action Input: 北京
~~~

步骤 3：执行与回调
程序调用天气 API，拿到结果“25度”，然后拼接回 Prompt，再次发给模型：
~~~text
...（上面的历史）
Observation: 25度，晴天
Thought: 我已经拿到结果了。
Final Answer: 北京现在天气晴朗，气温25度。
~~~

2. Function Calling
   Function Calling 实现逻辑不依赖复杂的提示词模板，而是依赖 API 的 tools 参数定义。

步骤 1：定义 Tools Schema
开发者直接向模型 API 发送一个 JSON 定义（无需包含在 System Prompt 文本里）：
~~~json
// 发送给 LLM 的请求结构
{
  "messages": [{"role": "user", "content": "查询北京天气"}],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string"}
          },
          "required": ["city"]
        }
      }
    }
  ]
}
~~~

步骤 2：模型原生判断
模型经过微调，识别到需要调用工具，它不再输出普通文本，而是返回一个特殊的标记（例如 finish_reason: "tool_calls"），并附带一个结构化的对象：
~~~json
// LLM 返回的响应
{
  "choice": {
    "finish_reason": "tool_calls",
    "message": {
      "tool_calls": [
        {
          "name": "get_weather",
          "arguments": "{\"city\": \"北京\"}"  // 这是一个完美的 JSON 字符串
        }
      ]
    }
  }
}
~~~

步骤 3：提交结果
程序执行 API，拿到结果，将结果封装成 role: "tool" 的消息发回给模型：
~~~json
[
  ...之前的消息,
  {
    "role": "tool",
    "tool_call_id": "call_123",
    "content": "25度，晴天"
  }
]
~~~
模型接收后，根据这个结果生成最终自然语言回复。

### 代码示例

#### ReAct
[代码](ReActDemo.py)

### Function calling
[代码](FunctionCallingDemo.py)

### 总结
Function Calling = 智能手机（操作简单，系统原生支持，点击APP即可）。如果你的业务追求速度和稳定，选 Function Calling。
ReAct = 命令行/DOS系统（你需要输入特定指令，看着屏幕一行行跑代码，虽然繁琐但能看到所有细节）。如果任务逻辑极其复杂（例如需要根据上一步结果动态决定下一步），且你需要调试模型的思路，选 ReAct。

### 扩展
[AgentSkills](../agentskills/README.md)