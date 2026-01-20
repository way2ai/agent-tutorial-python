import asyncio
from functools import wraps


def limit_concurrency_test(limit: int):
    sem = asyncio.Semaphore(limit)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # async with sem 意思是：
            # "尝试获取通行证。如果有，就进去执行 func；"
            # "如果没有，就在这里 await（排队），直到别人归还通行证。"
            async with sem:
                result = await func(*args, **kwargs)
                return result
        return wrapper
    return decorator

def getNowDateTime():
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H时%M分%S秒") + now.strftime("%f")[:3] + "毫秒"

@limit_concurrency_test(1)
# async:定义一个协程（可以暂停任务）
async def make_tea(customer_name: str):
    """
    点单.

    Args:
        customer_name: 顾客姓名
    
    Returns:
        None
    """
    print(f"给🧑 {customer_name} 点单.⌚️：{getNowDateTime()}")

    """
    await：
    1.它是一个信号。
    2.它标志着一个IO耗时操作（读文件、请求网页、连数据库）。
    3.它主动让出了 CPU，让程序去处理其他协程。
    """
    await asyncio.sleep(2)

    print(f"给🧑 {customer_name} 上茶.⌚️：{getNowDateTime()}")

async def main():
    tasks = [
        make_tea("张三"),
        make_tea("李四"),
        make_tea("王五"),
    ]

    print("--- 店铺开张 ---")
    await asyncio.gather(*tasks, return_exceptions=True)
    print("--- 全部搞定 ---")

if __name__ == "__main__":
    # 方式一：原始写法 
    # 1. 【创建】获取一个 Loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 2. 【运行】启动循环，直到 main() 结束
        # 经理在这里疯狂循环，直到 main 协程 return
        loop.run_until_complete(main())
    finally:
        # 3 & 4. 【停止与关闭】
        # 无论是否报错，都要确保经理下班关门
        loop.close()
        print("店铺关门，资源释放")

    # 方式二：现代写法 (Python 3.7+)
    # 【创建 -> 运行 -> 停止 -> 关闭】全部这一行搞定
    # asyncio.run(main())