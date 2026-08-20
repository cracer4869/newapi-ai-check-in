#!/usr/bin/env python3
"""
浏览器自动化相关的公共工具函数
"""

import os
import random
from datetime import datetime
from urllib.parse import urlparse


def parse_cookies(cookies_data) -> dict:
    """解析 cookies 数据

    支持字典格式和字符串格式的 cookies

    Args:
        cookies_data: cookies 数据，可以是字典或分号分隔的字符串

    Returns:
        解析后的 cookies 字典
    """
    if isinstance(cookies_data, dict):
        return cookies_data

    if isinstance(cookies_data, str):
        cookies_dict = {}
        for cookie in cookies_data.split(";"):
            if "=" in cookie:
                key, value = cookie.strip().split("=", 1)
                cookies_dict[key] = value
        return cookies_dict
    return {}


def filter_cookies(cookies: list[dict], origin: str) -> dict:
    """根据 origin 过滤 cookies，只保留匹配域名的 cookies

    Args:
        cookies: Camoufox cookies 列表，每个元素是包含 name, value, domain 等的字典
        origin: Provider 的 origin URL (例如: https://api.example.com)

    Returns:
        过滤后的 cookies 字典 {name: value}
    """
    # 提取 provider origin 的域名
    provider_domain = urlparse(origin).netloc

    # 过滤 cookies，只保留与 provider domain 匹配的
    user_cookies = {}
    matched_items = []  # 存储 "name(domain)" 格式
    filtered_items = []  # 存储 "name(domain)" 格式

    for cookie in cookies:
        cookie_name = cookie.get("name")
        cookie_value = cookie.get("value")
        cookie_domain = cookie.get("domain", "")

        if cookie_name and cookie_value:
            # 检查 cookie domain 是否匹配 provider domain
            # cookie domain 可能以 . 开头 (如 .example.com)，需要处理
            normalized_cookie_domain = cookie_domain.lstrip(".")
            normalized_provider_domain = provider_domain.lstrip(".")

            # 匹配逻辑：cookie domain 应该是 provider domain 的后缀
            if (
                normalized_provider_domain == normalized_cookie_domain
                or normalized_provider_domain.endswith("." + normalized_cookie_domain)
                or normalized_cookie_domain.endswith("." + normalized_provider_domain)
            ):
                user_cookies[cookie_name] = cookie_value
                matched_items.append(f"{cookie_name}({cookie_domain})")
            else:
                filtered_items.append(f"{cookie_name}({cookie_domain})")

    if matched_items:
        print(f"  🔵 Matched: {', '.join(matched_items)}")
    if filtered_items:
        print(f"  🔴 Filtered: {', '.join(filtered_items)}")

    print(
        f"🔍 Cookie filtering result ({provider_domain}): "
        f"{len(matched_items)} matched, {len(filtered_items)} filtered"
    )

    return user_cookies


def get_random_user_agent() -> str:
    """获取随机的现代浏览器 User Agent 字符串

    Returns:
        随机选择的 User Agent 字符串
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 " "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) " "Gecko/20100101 Firefox/134.0",
    ]
    return random.choice(user_agents)


async def take_screenshot(
    page,
    reason: str,
    account_name: str,
    screenshots_dir: str = "screenshots",
) -> None:
    """截取当前页面的屏幕截图

    Args:
        page: Camoufox/Playwright 页面对象
        reason: 截图原因描述
        account_name: 账号名称（用于日志输出和文件名）
        screenshots_dir: 截图保存目录，默认为 "screenshots"

    Note:
        通过环境变量 DEBUG=true 启用截图功能，默认为 false
    """
    # 检查 DEBUG 环境变量
    debug_enabled = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    if not debug_enabled:
        print(f"🔍 {account_name}: Screenshot skipped (DEBUG=false), reason: {reason}")
        return

    try:
        os.makedirs(screenshots_dir, exist_ok=True)

        # 自动生成安全的账号名称
        safe_account_name = "".join(c if c.isalnum() else "_" for c in account_name)

        # 生成文件名: 账号名_时间戳_原因.png
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_reason = "".join(c if c.isalnum() else "_" for c in reason)
        filename = f"{safe_account_name}_{timestamp}_{safe_reason}.png"
        filepath = os.path.join(screenshots_dir, filename)

        await page.screenshot(path=filepath, full_page=True)
        print(f"📸 {account_name}: Screenshot saved to {filepath}")
    except Exception as e:
        print(f"⚠️ {account_name}: Failed to take screenshot: {e}")


async def save_page_content_to_file(
    page,
    reason: str,
    account_name: str,
    prefix: str = "",
    logs_dir: str = "logs",
) -> None:
    """保存页面 HTML 到日志文件

    Args:
        page: Camoufox/Playwright 页面对象
        reason: 日志原因描述
        account_name: 账号名称（用于日志输出和文件名）
        prefix: 文件名前缀（如 "github_", "linuxdo_" 等）
        logs_dir: 日志保存目录，默认为 "logs"

    Note:
        通过环境变量 DEBUG=true 启用保存 HTML 功能，默认为 false
    """
    # 检查 DEBUG 环境变量
    debug_enabled = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    if not debug_enabled:
        print(f"🔍 {account_name}: Save HTML skipped (DEBUG=false), reason: {reason}")
        return

    try:
        os.makedirs(logs_dir, exist_ok=True)

        # 自动生成安全的账号名称
        safe_account_name = "".join(c if c.isalnum() else "_" for c in account_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_reason = "".join(c if c.isalnum() else "_" for c in reason)

        # 构建文件名
        if prefix:
            filename = f"{safe_account_name}_{timestamp}_{prefix}_{safe_reason}.html"
        else:
            filename = f"{safe_account_name}_{timestamp}_{safe_reason}.html"
        filepath = os.path.join(logs_dir, filename)

        html_content = await page.content()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"📄 {account_name}: Page HTML saved to {filepath}")
    except Exception as e:
        print(f"⚠️ {account_name}: Failed to save HTML: {e}")


async def aliyun_captcha_check(page, account_name: str) -> bool:
    """阿里云验证码检查和处理

    按页面特征检测阿里云 WAF 验证页（新版 Captcha 2.0 的 #captcha-element、旧版
    #nocaptcha、挑战页的 aliyun_waf_* meta，以及 #traceid 容器），命中则尝试自动滑动验证

    Args:
        page: Camoufox/Playwright 页面对象
        account_name: 账号名称（用于日志输出）

    Returns:
        bool: 验证码处理是否成功（无验证码或验证通过返回 True，验证失败返回 False）
    """
    # 检查是否命中阿里云验证码页面。
    # 旧逻辑只认 #traceid 里的 "TraceID: xxx" 文本，但 WAF 后台可以关掉 show_trace_id
    # （agentrouter 就关了），此时元素在、里面却只有时间没有 TraceID，验证码页会被
    # 当成正常页面直接放过。改为按页面特征判断。
    try:
        captcha_hit = await page.evaluate(
            """() => {
            const traceElement = document.getElementById('traceid');
            if (traceElement) {
                const text = traceElement.innerText || traceElement.textContent || '';
                const match = text.match(/TraceID:\\s*([a-f0-9]+)/i);
                if (match) return 'traceid:' + match[1];
            }
            // 新版 Captcha 2.0 渲染在 #captcha-element，旧版 nocaptcha 用 #nocaptcha
            if (document.getElementById('captcha-element')) return 'captcha-element';
            if (document.getElementById('nocaptcha')) return 'nocaptcha';
            // WAF 挑战页会插入这两个 meta
            if (document.querySelector('meta[name="aliyun_waf_aa"], meta[name="aliyun_waf_bb"]')) return 'waf-meta';
            // show_trace_id 关闭时只剩这个空容器
            if (traceElement) return 'traceid-empty';
            return null;
        }"""
        )

        if captcha_hit:
            print(f"⚠️ {account_name}: Aliyun captcha detected ({captcha_hit})")
            try:
                # 新旧两版都沿用 nc_scale / btn_slide 类名，只是父容器不同
                # （新版 #captcha-element，旧版 #nocaptcha），所以不限定父级
                await page.wait_for_selector(".nc_scale, #nocaptcha", timeout=60000)

                slider = None
                handle = None

                slider_element = await page.query_selector(".nc_scale")
                if slider_element:
                    slider = await slider_element.bounding_box()
                    print(f"ℹ️ {account_name}: Slider bounding box: {slider}")

                slider_handle = await page.query_selector(".btn_slide")
                if slider_handle:
                    handle = await slider_handle.bounding_box()
                    print(f"ℹ️ {account_name}: Slider handle bounding box: {handle}")

                if slider and handle:
                    await take_screenshot(page, "aliyun_captcha_slider_start", account_name)

                    start_x = handle.get("x") + handle.get("width") / 2
                    start_y = handle.get("y") + handle.get("height") / 2
                    target_x = handle.get("x") + slider.get("width")

                    await page.mouse.move(start_x, start_y)
                    await page.mouse.down()
                    # 分三段拖动、步数拉大，尽量避免被判成机器直线拖拽
                    await page.mouse.move(start_x + (target_x - start_x) * 0.6, start_y + 2, steps=18)
                    await page.wait_for_timeout(120)
                    await page.mouse.move(start_x + (target_x - start_x) * 0.9, start_y - 1, steps=10)
                    await page.wait_for_timeout(80)
                    await page.mouse.move(target_x, start_y, steps=6)
                    await page.mouse.up()
                    await take_screenshot(page, "aliyun_captcha_slider_completed", account_name)

                    # Wait for page to be fully loaded
                    await page.wait_for_timeout(20000)

                    await take_screenshot(page, "aliyun_captcha_slider_result", account_name)
                    return True
                else:
                    print(f"❌ {account_name}: Slider or handle not found")
                    await take_screenshot(page, "aliyun_captcha_error", account_name)
                    return False
            except Exception as e:
                print(f"❌ {account_name}: Error occurred while moving slider, {e}")
                await take_screenshot(page, "aliyun_captcha_error", account_name)
                return False
        else:
            print(f"ℹ️ {account_name}: No aliyun captcha detected")
            await take_screenshot(page, "aliyun_captcha_not_found", account_name)
            return True
    except Exception as e:
        print(f"❌ {account_name}: Error occurred while detecting aliyun captcha, {e}")
        await take_screenshot(page, "aliyun_captcha_error", account_name)
        return False
