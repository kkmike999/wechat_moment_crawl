import argparse
import sys
import os
from playwright.sync_api import sync_playwright
# https://github.com/Mattwmaster58/playwright_stealth
from playwright_stealth import Stealth

from params_utils import collect_urls
from playwright_utils import save_article_content


def main(initial_url: str | None = None, file_path: str | None = None):
    urls = collect_urls(initial_url, file_path)
    if urls is None:
        return

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
            #viewport={"width": 1080, "height": 1920},
            #screen={"width": 1080, "height": 1920},
            locale="zh-CN",  # 中文环境
        )
        
        page = context.new_page()

        # 注入 stealth 脚本隐藏自动化特征
        Stealth().apply_stealth_sync(page)

        # 读取temp/success_urls.txt
        success_urls = []
        with open(os.path.join(os.getcwd(), "temp", "success_urls.txt"), "r", encoding="utf-8") as f:
            success_urls = [line.strip() for line in f if line.strip()]
        
        try:
            for i, url in enumerate(urls, 1):
                # success_urls中存在的url不再访问
                if url in success_urls:
                    print(f"[{i}/{len(urls)}] 已访问过: {url}")
                    continue
                
                print(f"\n{'='*50}")
                print(f"[{i}/{len(urls)}] 开始访问: {url}")
                try:
                    result = save_article_content(page, url)
                    if result in (None, ""):
                        print("返回空，重试 1 次...")
                        result = save_article_content(page, url)
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