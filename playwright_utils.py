import time
from playwright.sync_api import Page


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
