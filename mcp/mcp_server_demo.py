
"""
Docstring for mcp.mcp_server_demo

需求：构建一个 简单的 MCP 天气服务器，并将其连接到一个 MCP 主机（Cherry Studio）

目标：
构建一个服务器，该服务器将暴露两个工具： get_alerts 和 get_forecast 。
然后我们将该服务器连接到一个 MCP 主机（Cherry Studio）

方案：使用 FastMCP 来快速构建 MCP 服务器
# 1.创建环境并安装依赖（参考：https://github.com/zh4ngyj/my-docs/blob/main/miniconda/README.md）
# 1.1.创建 conda 环境 mcp (推荐使用miniconda)
~~~bash
conda create -n mcp python=3.10 -y
~~~bash
# 1.2.安装 uv
~~~bash
# 方法A: (推荐) 系统级安装，此时 uv 会自动检测当前激活的 conda 环境
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 方法B: 在当前 conda 环境里装
pip install uv
~~~
# 1.3.进入 mcp 目录
~~~bash
cd path/to/mcp
~~~
# 1.4.安装 mcp 相关包
~~~bash
# 激活 conda 环境
conda activate mcp

# 使用 pip 安装 mcp 及其 cli 依赖
uv pip install mcp[cli] httpx
~~~
# 2.编写代码 mcp/mcp_server_demo.py
# 3.运行 MCP 服务器 demo

验证：
1.运行 cherry-studio 桌面版
2.注册 MCP Server 到 cherry-studio
类型 (Type): Stdio
名称 (Name): WeatherServer
命令 (Command): path/to/miniconda3/envs/mcp/python.exe
参数 (Arguments): path/to/mcp_server_demo.py
3.通过 cherry-studio 进行测试 MCP Server
选择一个支持工具调用的模型,添加 WeatherServer 到工具中，直接用自然语言提问，模型会自动决定调用哪个工具。
"""
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
AMAP_API_V3_BASE = "https://restapi.amap.com/v3"
KEY = "e82e58358bcc83fb54c5c4b86f52530b"
EXTENSIONS = ("base", "all")
OUTPUT =("JSON", "XML")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

@mcp.tool()
async def get_adcode(address: str) -> int:
    """
    Get the adcode for a given address.

    Args:
        address (str): The address to get adcode for.(e.g. "北京市朝阳区阜通东大街6号")
    Returns:
        int: adcode of address.(e.g. 110105, -1 if not found)
    """
    url = f"{AMAP_API_V3_BASE}/geocode/geo?address={address}&key={KEY}"
    data = await make_request(url)

    if not data or "geocodes" not in data or len(data["geocodes"]) == 0:
        return -1
    
    adcode = data["geocodes"][0].get("adcode", -1)
    
    logger.info(f"Address: {address}, Adcode: {adcode}")
    return int(adcode)

@mcp.tool()
async def get_weather_lives(adcode: int) -> str:
    """
    Get live weather information for a given adcode.

    Args:
        adcode (int): The adcode to get weather information for.(e.g. 110105)
    Returns:
        str: Formatted live weather information.
    """
    url = f"{AMAP_API_V3_BASE}/weather/weatherInfo?city={adcode}&key={KEY}&extensions={EXTENSIONS[0]}&output={OUTPUT[0]}"
    data = await make_request(url)

    if not data or "lives" not in data or len(data["lives"]) == 0:
        return "No live weather data found."

    live = data["lives"][0]
    formatted_live = format_live(live)
    
    logger.info(f"Live weather for adcode {adcode}: {formatted_live}")
    return formatted_live

@mcp.tool()
async def get_weather_forecast(adcode: int) -> str:
    """
    Get weather forecast for a given adcode.

    Args:
        adcode (int): The adcode to get weather forecast for.(e.g. 110105)  
    Returns:
        str: Formatted weather forecast information.
    """
    url = f"{AMAP_API_V3_BASE}/weather/weatherInfo?city={adcode}&key={KEY}&extensions={EXTENSIONS[1]}&output={OUTPUT[0]}"
    data = await make_request(url)

    if not data or "forecasts" not in data or len(data["forecasts"]) == 0:
        return "No weather forecast data found."

    forecasts = data["forecasts"][0]
    city_forecasts = forecasts.get("casts", [])

    if not city_forecasts:
        return "No weather forecast data found."
    
    formatted_forecast = [format_forecast(forecast) for forecast in city_forecasts]
    formatted_forecast = "\n---\n".join(formatted_forecast)

    logger.info(f"Weather forecast for adcode {adcode}: {formatted_forecast}")
    return formatted_forecast

@mcp.tool()
async def get_nowdate() -> str:
    """Get the current date in YYYY-MM-DD format."""
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y-%m-%d")

@mcp.tool()
async def ping() -> str:
    """A simple ping tool to check server responsiveness."""
    return "Pong!"

async def make_request(url: str) -> dict[str, Any] | None:
    """Make an asynchronous GET request and return the JSON response."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers, timeout=3.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.error(f"Request to {url} failed.", exc_info=True)
            return None
        
def format_live(live: dict) -> str:
    """Format live weather alert information into a readable string."""
    return f"""
省份: {live.get('province', 'Unknown')}
城市: {live.get('city', 'Unknown')}
天气: {live.get('weather', 'Unknown')}
气温: {live.get('temperature', 'No temperature available')}
风向: {live.get('winddirection', 'No winddirection available')}
风力: {live.get('windpower', 'No windpower available')}
湿度: {live.get('humidity', 'No humidity available')}
报告时间: {live.get('reporttime', 'No report time available')}
"""

def format_forecast(forecast: dict) -> str:
    """Format weather forecast information into a readable string."""
    return f"""
日期: {forecast.get('date', 'Unknown')}
星期几: {forecast.get('week', 'Unknown')}
白天天气: {forecast.get('dayweather', 'No dayweather available')}
夜间天气: {forecast.get('nightweather', 'No nightweather available')}
白天温度: {forecast.get('daytemp', 'No daytemp available')}
夜间温度: {forecast.get('nighttemp', 'No nighttemp available')}
白天风向: {forecast.get('daywind', 'No daywind available')}
夜间风向: {forecast.get('nightwind', 'No nightwind available')}
白天风力: {forecast.get('daypower', 'No daypower available')}
夜间风力: {forecast.get('nightpower', 'No nightpower available')}
"""

def main():
    # Initialize and run the MCP server
    mcp.run(transport="stdio")

    # Initialize and run the MCP server by SSE (http://127.0.0.1:8000/sse)
    # mcp.run(transport="sse")

    # Initialize and run the MCP server by StreamableHttp (http://127.0.0.1:8000/mcp)
    # mcp.run(transport="streamable-http")

if __name__ == "__main__":
    logger.info("Starting MCP Weather Server...")
    main()