"Agent Skills"（智能体技能） 确实是一个非常核心的概念，尤其是在更高级的 Agent 开发框架（如 Microsoft 的 Semantic Kernel、Coze、或者 LangChain 的某些场景）中经常出现。
如果把 Agent 比作一个**“打工人”**：
Agent 策略 (ReAct/Function Calling) 是它的**“工作思维”**（遇到问题先思考还是先动手）。
LLM (大模型) 是它的**“大脑”**（智商基础）。
Agent Skills (技能) 就是它的**“专业证书”或“工具包”**。


Skill 的两种主要形式
在 Agent 开发（特别是 Microsoft Semantic Kernel）中，Skill 被明确分为两类，这非常重要：
1. Semantic Skills（语义技能 / 软技能）
这是由 Prompt（提示词）定义的技能。
原理：你不需要写代码，只需要写好一个特定的 Prompt 模板。
场景：翻译、润色文章、写笑话、情感分析。
示例：你定义一个“翻译技能”，内容就是 请将下面的文本翻译成英文：{{$input}}。对 Agent 来说，这也是一个可以调用的 Skill。
2. Native Skills（原生技能 / 硬技能）
这是由代码（Python/C#/Java）定义的技能。
原理：这就是前面说的 Function Calling，真刀真枪去跑代码。
场景：查数据库、发HTTP请求、数学计算、操作文件。

为什么需要提出 Skills 这个概念？
有了 Function Calling 为什么还要造一个 Skills 词汇？主要是为了**“复用”和“编排”**。
1. 模块化管理
如果你开发了一个复杂的 Agent，它可能有 100 个工具。如果不分组，Prompt 会爆炸（Token 超限），模型也会晕。
引入 Skill 后，你可以这样管理：
MathSkill (包含 add, sqrt, sin...)
FileSkill (包含 read, write, delete...)
SearchSkill (包含 google, bing...)
Agent 可以根据任务，先加载 MathSkill，卸载 FileSkill，这样更高效。
2. 混合编排（Prompt + Code）
Skill 允许把“写代码”和“写提示词”统一看待。
比如一个 “写周报 Skill” 的内部流程可能是：
调用 DatabaseSkill.get_data() (代码：拉取本周数据)
调用 WriterSkill.summarize() (Prompt：把数据润色成通顺的文字)
调用 EmailSkill.send() (代码：发送给老板)
对 Agent 来说，这三个都是 Skill 下的 Function，调用方式一模一样。

代码示例

总结
策略 (ReAct/Function Calling)：决定了 Agent 怎么去调用。
Skills (技能)：定义了 Agent 能调用什么（是去调一个 API，还是去调一个写好的 Prompt 模板）。
在现在的产品界面（如 Dify、FastGPT）中，"Skills" 往往演变成了 "插件 (Plugins)" 或 "工具库" 的概念。如果你看到 "Add Skill"（添加技能），通常意味着你可以给这个 Agent 挂载一个 Google 搜索插件、或者挂载一个专门写代码的 Python 解释器。