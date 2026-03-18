import argparse
import os
import re
import sys
from playwright.sync_api import sync_playwright
# https://github.com/Mattwmaster58/playwright_stealth
from playwright_stealth import Stealth

from playwright_utils import visit_and_wait_for_content


def save_article_content(page, initial_url: str) -> str:
    """访问URL、获取页面内容并保存到 temp/<title>.html"""
    visit_and_wait_for_content(page, initial_url)

    current_url = page.url
    print(f"[2/5] 当前URL: {current_url}")
    print("[3/5] 页面加载完成")
    print("[4/5] 获取内容...")

    content = page.content()
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    title = page.title() or "weixin_article"
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", title.strip())[:200]
    filename = f"{safe_name}.html" if safe_name else "weixin_article.html"
    output_file = os.path.join(temp_dir, filename)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[5/5] 成功保存到: {output_file}")
    print(f"    文件大小: {len(content):,} 字符")
    print(f"    {'✓ 包含 #js_content' if 'js_content' in content else '⚠ 可能加载失败'}")
    return output_file


def main(initial_url: str | None = None, file_path: str | None = None):
    urls: list[str] = []
    # 若只传了 positional 参数且为已存在的文件，视为文件路径
    if file_path is None and initial_url and os.path.isfile(initial_url):
        file_path = initial_url
        initial_url = None
    if file_path:
        # 从文件读取 URL，每行一个
        if not os.path.isfile(file_path):
            print(f"文件不存在: {file_path}")
            return
        with open(file_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        if not urls:
            print("文件中没有有效的 URL")
            return
        print(f"从文件读取到 {len(urls)} 个 URL")
    elif initial_url:
        urls = [initial_url]
    else:
        print("请传入要爬取的公众号文章URL或文件路径")
        user_input = input("请输入URL或文件路径: ").strip()
        if not user_input:
            print("未输入，已退出")
            return
        if os.path.isfile(user_input):
            with open(user_input, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            if not urls:
                print("文件中没有有效的 URL")
                return
            print(f"从文件读取到 {len(urls)} 个 URL")
        else:
            urls = [user_input]
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=False,  # 设置为True可无头运行
            args=['--disable-blink-features=AutomationControlled']  # 隐藏自动化特征
        )

        # 根据本机系统选择 user_agent
        user_agent = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            if sys.platform == 'darwin'
            else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1080, "height": 1920},  # Windows 常见分辨率
            screen={"width": 1080, "height": 1920},
            locale="zh-CN",  # 中文环境
        )
        
        page = context.new_page()

        # 注入 stealth 脚本隐藏自动化特征
        Stealth().apply_stealth_sync(page)
        
        try:
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*50}")
                print(f"[{i}/{len(urls)}] 开始访问: {url}")
                try:
                    save_article_content(page, url)
                except Exception as e:
                    print(f"错误: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="微信公众号文章爬虫")
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="要爬取的公众号文章URL，或 URL 列表文件路径（每行一个 URL）",
    )
    parser.add_argument(
        "-f", "--file",
        dest="file_path",
        default=None,
        help="URL 列表文件路径，每行一个 URL",
    )
    args = parser.parse_args()
    main(initial_url=args.url, file_path=args.file_path)