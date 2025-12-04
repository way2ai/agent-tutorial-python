# Model Context Protocol (MCP)

## Overview 简介
MCP（模型上下文协议）是一个用于将人工智能应用连接到外部系统的开源标准。

使用 MCP，AI 应用如 Claude 或 ChatGPT 可以连接到数据源（例如本地文件、数据库）、工具（例如搜索引擎、计算器）和工作流（例如专用提示），从而能够访问关键信息并执行任务。

![mcp](mcp-simple-diagram.avif)

MCP 能干什么？
- 智能体可以访问您的 Google 日历和 Notion，充当更加个性化的 AI 助手。
- Claude 代码可以使用 Figma 设计生成一个完整的网页应用。
- 企业聊天机器人可以连接组织内的多个数据库，使用户能够通过聊天分析数据。
- 人工智能模型可以在 Blender 上创建 3D 设计并使用 3D 打印机将其打印出来。
- 开发者：MCP 在构建或与 AI 应用或代理集成时，能够减少开发时间和复杂性。
- 人工智能应用或代理：MCP 提供对数据源、工具和应用程序的生态系统访问，从而增强能力并提升最终用户的体验。
- 终端用户：MCP 使 AI 应用或代理更加强大，能够访问您的数据并在必要时代表您采取行动。

## Architecture 架构

### Participants 参与者
MCP 采用客户端-服务器架构，其中 MCP 主机——如 Claude Code 或 Claude Desktop 等 AI 应用——会连接一个或多个 MCP 服务器。MCP 主机通过为每个 MCP 服务器创建一个 MCP 客户端来实现这一连接。每个 MCP 客户端与其对应的 MCP 服务器保持专用的一对一连接。

参与者包含：
- MCP Host：协调和管理一个或多个 MCP 客户端的 AI 应用
- MCP Client：维护与 MCP 服务器连接并从 MCP 服务器获取上下文供 MCP 主机使用的组件
- MCP Server：向 MCP 客户端提供上下文的程序

例如：Visual Studio Code 充当 MCP 主机。当 Visual Studio Code 连接到 MCP 服务器（如 Sentry MCP 服务器）时，Visual Studio Code 运行时会创建一个 MCP 客户端对象以维持与 Sentry MCP 服务器的连接。当 Visual Studio Code 随后连接到另一个 MCP 服务器（如本地文件系统服务器）时，运行时会创建另一个 MCP 客户端对象以维持该连接，从而保持 MCP 客户端与 MCP 服务器之间的一一对应关系。

MCP 服务器可以按照运行位置进行分类。可以是本地 MCP服务器，比如本地运行的处理文件的文件系统服务器。也可以是远程服务器，比如官方 Sentry MCP 服务器在 Sentry 平台上运行。

### Layer Structure 层级结构
- 数据层：定义基于 JSON-RPC 的客户端-服务器通信协议，包括生命周期管理，以及核心基础元素，如工具、资源、提示和通知。
- 传输层：定义了通信机制和通道，使客户端和服务器之间能够进行数据交换，包括特定传输协议的连接建立、消息帧格式和授权机制。

**Data layer 数据层**：数据层实现了一个基于 JSON-RPC 2.0 的交换协议，定义了消息结构和语义。
- 生命周期管理：处理客户端与服务器之间的连接初始化、能力协商和连接终止
- 服务器功能：使服务器能够向客户端提供核心功能，包括用于 AI 操作的工具、用于上下文数据的资源以及用于交互模板的提示
- 客户端功能：使服务器能够请求客户端从主机 LLM 中进行采样、获取用户输入并记录消息到客户端
- 实用功能：支持额外功能，如实时更新的通知和长时间运行操作的进度跟踪

**Transport layer 传输层**：传输层管理客户端与服务器之间的通信通道和认证。它负责连接建立、消息封装以及 MCP 参与者之间的安全通信。
- **Stdio 传输**：使用标准输入/输出流在同一台机器上的本地进程之间进行直接通信，提供最优性能且无网络开销。
- **Streamable HTTP 传输**：使用 HTTP POST 用于客户端到服务器的消息传递，并可选地使用 Server-Sent Events 实现流式功能。该传输方式支持与远程服务器的通信，并且支持标准的 HTTP 认证方法，包括 bearer token、API 密钥和自定义头信息。MCP 推荐使用 OAuth 来获取认证令牌。

### Primitives 基本元素
MCP 基本元素是 MCP 中最核心的概念。它们定义了客户端和服务器可以相互提供的功能。这些基本元素指定了可以与 AI 应用共享的上下文信息类型以及可以执行的操作范围。

MCP 服务器可以暴露的三个核心基本元素：
- 工具：AI 应用可以调用以执行操作的可执行函数（例如，文件操作、API 调用、数据库查询）
- 资源：为 AI 应用提供上下文信息的数据源（例如，文件内容、数据库记录、API 响应）
- 提示：可重用的模板，用于帮助与语言模型进行交互（例如，系统提示、少样本示例）

每种原始类型都有与之关联的方法用于发现（ */list ）、检索（ */get ）以及在某些情况下执行（ tools/call ）。MCP 客户端将使用 */list 方法来发现可用的原始类型。例如，客户端可以首先列出所有可用的工具（ tools/list ），然后执行它们。这种设计使得列表具有动态性

作为一个具体的例子，考虑一个提供数据库上下文的 MCP 服务器。它可以暴露用于查询数据库的工具、包含数据库模式的资源，以及包含与工具交互的少样本示例的提示。

MCP 还定义了客户端可以暴露的基本元素：
- 采样：允许服务器从客户端的 AI 应用请求语言模型的补全。当服务器作者希望访问语言模型但又希望保持模型无关性，并且不想在其 MCP 服务器中包含语言模型 SDK 时，这一功能非常有用。他们可以使用 sampling/complete 方法从客户端的 AI 应用请求语言模型补全。
- 引出：允许服务器从用户处请求附加信息。当服务器的作者希望从用户获取更多信息或确认某个操作时，这非常有用。他们可以使用 elicitation/request 方法向用户请求附加信息。
- 日志记录：使服务器能够向客户端发送日志消息，用于调试和监控目的。

### Notifications 通知
该协议支持实时通知，以实现服务器与客户端之间的动态更新。例如，当服务器的可用工具发生变化时（如新功能上线或现有工具被修改），服务器可以发送工具更新通知，以告知已连接的客户端这些变化。通知以 JSON-RPC 2.0 通知消息的形式发送（无需响应），并使 MCP 服务器能够向已连接的客户端提供实时更新。

## Example 示例
逐步演示 MCP 客户端-服务器交互过程，重点介绍数据层协议。

1.Initialzation (Lifecycle Management) 初始化（生命周期管理）: MCP 通过一种能力协商握手来开始生命周期管理。如生命周期管理部分所述，客户端发送一个 initialize 请求以建立连接并协商支持的功能。

~~~json
# 初始化请求
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "elicitation": {}
    },
    "clientInfo": {
      "name": "example-client",
      "version": "1.0.0"
    }
  }
}
~~~

在初始化过程中，AI 应用的 MCP 客户端管理器会与配置的服务器建立连接，并存储其功能能力以备后续使用。应用利用这些信息来判断哪些服务器可以提供特定类型的功能（工具、资源、提示）以及它们是否支持实时更新。

2.Tool Discovery (Primitives) 工具发现 （基本元素）: 现在连接已建立，客户端可以通过发送 tools/list 请求来发现可用的工具。该请求是 MCP 工具发现机制的基础——它允许客户端在尝试使用工具之前了解服务器上可用的工具。

~~~json
# 工具列表请求
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}

# 工具列表响应
#响应中包含一个 tools 数组，该数组提供了有关每个可用工具的全面元数据。
~~~

3. Tool Execution (Primitives) 工具执行 (基本操作)：客户端现在可以使用 tools/call 方法执行工具。这展示了 MCP 基本操作在实际中的使用方式：在发现可用工具后，客户端可以使用适当的参数调用它们。

~~~json
# 工具调用请求
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "weather_current",
    "arguments": {
      "location": "San Francisco",
      "units": "imperial"
    }
  }
}

# 请求参数解释：
# name ：必须与发现响应中的工具名称（ weather_current ）完全匹配
# arguments ：包含由工具的 inputSchema 定义的输入参数。
# JSON-RPC 结构：使用标准的 JSON-RPC 2.0 格式，并通过唯一的 id 标识符实现请求-响应关联。

# 工具调用响应
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in San Francisco: 68°F, partly cloudy with light winds from the west at 8 mph. Humidity: 65%"
      }
    ]
  }
}
# 响应参数解释：
# content（数组）：工具响应返回内容对象的数组，允许进行丰富、多格式的响应（文本、图像、资源等）

~~~

TODO: 
https://modelcontextprotocol.io/docs/learn/architecture#understanding-the-tool-execution-response
1.~~~标签中增加响应示例
2.补充参数说明