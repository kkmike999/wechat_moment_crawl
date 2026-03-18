import argparse
import os
from playwright.sync_api import sync_playwright

from playwright_utils import visit_and_wait_for_content


def main(initial_url: str | None = None):
    if initial_url is None:
        print("请传入要爬取的公众号文章URL")
        initial_url = input("请输入URL: ").strip()
        if not initial_url:
            print("未输入URL，已退出")
            return
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=False,  # 设置为True可无头运行
            args=['--disable-blink-features=AutomationControlled']  # 隐藏自动化特征
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        
        page = context.new_page()
        
        print(f"[1/5] 开始访问: {initial_url}")
        
        try:
            visit_and_wait_for_content(page, initial_url)
            
            current_url = page.url
            print(f"[2/5] 当前URL: {current_url}")
            print("[3/5] 页面加载完成")
            print("[4/5] 获取内容...")
            
            # 获取并保存内容
            content = page.content()
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            output_file = os.path.join(temp_dir, "weixin_article.html")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"[5/5] 成功保存到: {output_file}")
            print(f"    文件大小: {len(content):,} 字符")
            print(f"    {'✓ 包含 #js_content' if 'js_content' in content else '⚠ 可能加载失败'}")
                
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
        help="要爬取的公众号文章URL（不传则会在运行时提示输入）",
    )
    args = parser.parse_args()
    main(initial_url=args.url)