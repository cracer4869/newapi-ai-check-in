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


async def dump_captcha_dom(page, account_name: str, logs_dir: str = "logs") -> None:
    """把验证码页渲染后的 DOM（含所有 iframe）落盘

    验证码厂商改版时，靠日志只能看到"没找到滑块"，看不出结构变成了什么样。
    DEBUG=true 时把每个 frame 的 HTML 存下来，随 artifact 上传，便于定位。

    Args:
        page: Camoufox/Playwright 页面对象
        account_name: 账号名称（用于日志输出和文件名）
        logs_dir: 保存目录，默认为 "logs"
    """
    if os.getenv("DEBUG", "false").lower() not in ("true", "1", "yes"):
        return

    try:
        os.makedirs(logs_dir, exist_ok=True)
        safe_account_name = "".join(c if c.isalnum() else "_" for c in account_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(logs_dir, f"{safe_account_name}_{timestamp}_captcha_dom.html")

        frames = page.frames
        parts = [f"<!-- page url: {page.url} | frames: {len(frames)} -->"]
        for idx, frame in enumerate(frames):
            try:
                content = await frame.content()
            except Exception as e:
                content = f"<!-- frame content unavailable: {e} -->"
            parts.append(f"\n\n<!-- ===== frame[{idx}] url={frame.url} ===== -->\n{content}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("".join(parts))

        print(f"ℹ️ {account_name}: Captcha DOM dumped to {filepath} ({len(frames)} frame(s))")
    except Exception as e:
        print(f"⚠️ {account_name}: Unable to dump captcha DOM: {e}")


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
                # 新版 Captcha 2.0 的滑块用 id 挂在主 DOM 上（#aliyunCaptcha-sliding-*），
                # 不是旧版 nocaptcha 的 .nc_scale/.btn_slide 类名，两套都试。
                # 仍然逐 frame 找，以防某些站点用 popup 模式渲染进 iframe；
                # bounding_box 由 Playwright 换算成主页面坐标，鼠标操作不用改。
                # sliding-body 是可见滑轨（SDK 里 slideStyle.width 就是它，约 300px），
                # sliding-wrapper 是外层容器、宽一倍多，拿它算终点会冲过滑轨末端
                track_selectors = ("#aliyunCaptcha-sliding-body", "#aliyunCaptcha-sliding-wrapper", ".nc_scale")
                handle_selectors = ("#aliyunCaptcha-sliding-slider", ".btn_slide")

                slider = None
                handle = None

                for _ in range(10):
                    for frame in page.frames:
                        try:
                            track_el = None
                            for selector in track_selectors:
                                track_el = await frame.query_selector(selector)
                                if track_el:
                                    break
                            if not track_el:
                                continue

                            handle_el = None
                            for selector in handle_selectors:
                                handle_el = await frame.query_selector(selector)
                                if handle_el:
                                    break
                            if not handle_el:
                                continue

                            slider = await track_el.bounding_box()
                            handle = await handle_el.bounding_box()
                            if slider and handle:
                                print(f"ℹ️ {account_name}: Slider found in frame: {frame.url[:100]}")
                                break
                        except Exception:
                            continue
                    if slider and handle:
                        break
                    await page.wait_for_timeout(2000)

                if slider:
                    print(f"ℹ️ {account_name}: Slider bounding box: {slider}")
                if handle:
                    print(f"ℹ️ {account_name}: Slider handle bounding box: {handle}")

                if slider and handle:
                    await take_screenshot(page, "aliyun_captcha_slider_start", account_name)

                    start_x = handle.get("x") + handle.get("width") / 2
                    start_y = handle.get("y") + handle.get("height") / 2
                    # 终点取滑轨右端减半个手柄宽。上一版用 handle.x + track.width，
                    # 在 wrapper 上算出来会冲过可见滑轨末端几百像素，必然判失败
                    target_x = slider.get("x") + slider.get("width") - handle.get("width") / 2

                    print(f"ℹ️ {account_name}: Dragging slider {start_x:.0f} -> {target_x:.0f}")

                    await page.mouse.move(start_x, start_y)
                    await page.mouse.down()
                    # Camoufox 的 humanize 已经在插值鼠标轨迹，steps 再拉大会让一次拖动
                    # 耗时几十秒（上一版实测 36 秒），反而被判超时，所以保持小步数
                    await page.mouse.move(target_x, start_y, steps=3)
                    await page.mouse.up()
                    await take_screenshot(page, "aliyun_captcha_slider_completed", account_name)

                    # 等验证结果回来并跳转
                    await page.wait_for_timeout(12000)

                    await take_screenshot(page, "aliyun_captcha_slider_result", account_name)
                    return True
                else:
                    print(f"❌ {account_name}: Slider or handle not found")
                    # 轮询结束后再落盘，此时 SDK 已渲染完，DOM 才反映真实结构
                    await dump_captcha_dom(page, account_name)
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
