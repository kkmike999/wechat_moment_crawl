import os
import re
import time
from playwright.sync_api import Page

from html_to_markdown import html_to_markdown


def visit_and_wait_for_content(page: Page, url: str) -> None:
    """
    访问网页并等待内容加载完成。
    处理验证码重定向和文章内容加载。
    """
    # 访问初始URL，等待DOM加载
    page.goto(url, wait_until="domcontentloaded")
    time.sleep(2)

    current_url = page.url

    # 处理验证码页面重定向
    if "wappoc_appmsgcaptcha" in current_url:
        page.wait_for_load_state("networkidle")
        time.sleep(3)
    else:
        pass  # 无需验证码，直接继续

    # 等待文章内容加载
    try:
        page.wait_for_selector("#js_content", state="visible", timeout=20000)
    except Exception:
        page.wait_for_load_state("networkidle", timeout=20000)

    time.sleep(3)  # 额外等待JS渲染


def save_article_content(page: Page, url: str) -> str:
    """访问URL、获取页面内容并保存到 temp/<title>.md"""
    visit_and_wait_for_content(page, url)

    # current_url可能重定向过
    current_url = page.url
    print(f"[2/5] 当前URL: {current_url}")
    print("[3/5] 页面加载完成")
    print("[4/5] 获取内容...")

    js_article = page.locator("#js_article.rich_media")
    has_js_article = js_article.count() > 0
    if has_js_article:
        print("✓ 已提取 #js_article")
        page.locator(".rich_media_area_extra, #js_tags_preview_toast, #content_bottom_area, .wx_bottom_modal_wrp.font-pannel-modal, #wx_stream_article_slide_tip").evaluate_all("nodes => nodes.forEach(n => n.remove())")
        content = js_article.inner_html()
    else:
        print("⚠ 未找到 #js_article，使用整页")
        content = page.content()

    # 创建 temp 目录
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    if "当前环境异常，完成验证后即可继续访问" in content:
        print("错误：微信页面需要验证，请完成验证后重试")
        
        with open(os.path.join(temp_dir, "error_urls.txt"), "a", encoding="utf-8") as f:
            f.write(url + "\n")
        return None

    content = html_to_markdown(content)
    
    title = page.title() or "weixin_article"
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", title.strip())[:200]

    filename = f"{safe_name}.md" if safe_name else "weixin_article.md"
    output_file = os.path.join(temp_dir, filename)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[5/5] 成功保存到: {output_file}")
    print(f"    文件大小: {len(content):,} 字符")
    print(f"    {'✓ 已提取 #js_article' if has_js_article else '⚠ 未找到 #js_article，使用整页'}")

    # 将url写入 temp/success_urls.txt
    with open(os.path.join(temp_dir, "success_urls.txt"), "a", encoding="utf-8") as f:
        f.write(current_url + "\n")

    return output_file
