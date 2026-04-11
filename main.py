"""
课程表每日推送脚本
使用 Playwright 自动化查询 SeaTable 授课查询页面
通过 Server酱 推送微信通知
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import urllib.request
import urllib.parse


async def query_courses(date_str: str) -> list:
    """
    查询指定日期的课程
    
    Args:
        date_str: 日期字符串，格式 YYYY-MM-DD
    
    Returns:
        课程列表
    """
    courses = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            # 访问授课查询页面
            await page.goto(
                "https://cloud.seatable.cn/external-apps/aa731c40-006f-439c-99b8-cae69fa483eb/?page_id=8n27",
                wait_until="networkidle",
                timeout=60000
            )
            
            # 等待页面加载
            await page.wait_for_timeout(2000)
            
            # 填写学校（第一个输入框）
            inputs = await page.query_selector_all('input[type="text"]')
            if len(inputs) >= 1:
                await inputs[0].fill("南京大学")
                await inputs[0].dispatch_event("input")
            
            await page.wait_for_timeout(500)
            
            # 填写班级（第二个输入框）
            if len(inputs) >= 2:
                await inputs[1].fill("23临床")
                await inputs[1].dispatch_event("input")
            
            await page.wait_for_timeout(500)
            
            # 填写日期（第三个输入框）
            if len(inputs) >= 3:
                await inputs[2].fill(date_str)
                await inputs[2].dispatch_event("input")
            
            await page.wait_for_timeout(500)
            
            # 点击查询按钮
            await page.get_by_role("button", name="查询", exact=True).click()
            
            # 等待查询结果
            await page.wait_for_timeout(3000)
            
            # 获取页面快照
            content = await page.content()
            
            # 解析结果
            if "没有记录" in content:
                print(f"[{date_str}] 没有课程")
            else:
                # 尝试提取课程数据
                rows = await page.query_selector_all("table tbody tr, .row, [class*='record']")
                for row in rows:
                    text = await row.inner_text()
                    if text.strip():
                        courses.append(text.strip())
                
                # 备用方案：直接获取表格文本
                if not courses:
                    table = await page.query_selector("table")
                    if table:
                        table_text = await table.inner_text()
                        if "没有记录" not in table_text and len(table_text) > 10:
                            courses.append(table_text)
            
            print(f"[{date_str}] 查询完成，找到 {len(courses)} 条记录")
            
        except Exception as e:
            print(f"[{date_str}] 查询出错: {e}")
        finally:
            await browser.close()
    
    return courses


def format_courses_message(date_str: str, courses: list) -> str:
    """格式化课程消息"""
    if not courses:
        return f"📅 **{date_str}**\n🎉 今天没有课程安排，好好休息！"
    
    message = f"📅 **{date_str}** 课程安排\n\n"
    message += "─" * 20 + "\n"
    
    for i, course in enumerate(courses, 1):
        message += f"{i}. {course}\n"
    
    message += "─" * 20
    return message


async def main():
    """主函数"""
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"开始查询课程表: {today}, {tomorrow}")
    
    # 查询今天和明天的课程
    today_courses = await query_courses(today)
    tomorrow_courses = await query_courses(tomorrow)
    
    # 格式化消息
    today_msg = format_courses_message(today, today_courses)
    tomorrow_msg = format_courses_message(tomorrow, tomorrow_courses)
    
    # 组合完整消息
    full_message = f"📚 课程表提醒\n\n{today_msg}\n\n{tomorrow_msg}\n\n⏰ 来自自动化课程查询系统"
    
    # 输出消息（供 GitHub Actions 或其他渠道使用）
    print("\n" + "=" * 40)
    print(full_message)
    print("=" * 40)
    
    # 保存到文件供后续处理
    with open("course_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "today": {"date": today, "courses": today_courses, "message": today_msg},
            "tomorrow": {"date": tomorrow, "courses": tomorrow_courses, "message": tomorrow_msg},
            "full_message": full_message,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    # 通过 Server酱 发送微信通知
    serverchan_key = os.environ.get("SERVERCHAN_KEY", "")
    if serverchan_key:
        send_serverchan(full_message, serverchan_key)
    else:
        print("⚠️ 未设置 SERVERCHAN_KEY，请配置后重试")
    
    return full_message


def send_serverchan(message: str, key: str) -> bool:
    """通过 Server酱 发送微信通知"""
    if not key:
        print("⚠️ 未配置 SERVERCHAN_KEY，跳过微信推送")
        return False
    
    try:
        url = f"https://sctapi.ftqq.com/{key}.send"
        data = urllib.parse.urlencode({
            "title": "📚 课程表提醒",
            "desp": message
        }).encode("utf-8")
        
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            
        if result.get("code") == 0:
            print("✅ 微信推送发送成功！")
            return True
        else:
            print(f"❌ 微信推送失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(main())
