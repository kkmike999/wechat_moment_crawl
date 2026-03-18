import os


def collect_urls(
    initial_url: str | None = None,
    file_path: str | None = None,
) -> list[str] | None:
    """从参数或交互输入收集要爬取的 URL 列表。失败或取消时返回 None。"""
    urls: list[str] = []

    # 若只传了 positional 参数且为已存在的文件，视为文件路径
    if file_path is None and initial_url and os.path.isfile(initial_url):
        file_path = initial_url
        initial_url = None

    if file_path:
        # 从文件读取 URL，每行一个
        if not os.path.isfile(file_path):
            print(f"文件不存在: {file_path}")
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        if not urls:
            print("文件中没有有效的 URL")
            return None
        print(f"从文件读取到 {len(urls)} 个 URL")
        
    elif initial_url:
        urls = [initial_url]
    else:
        print("请传入要爬取的公众号文章URL或文件路径")
        user_input = input("请输入URL或文件路径: ").strip()
        if not user_input:
            print("未输入，已退出")
            return None
        if os.path.isfile(user_input):
            with open(user_input, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            if not urls:
                print("文件中没有有效的 URL")
                return None
            print(f"从文件读取到 {len(urls)} 个 URL")
        else:
            urls = [user_input]
    return urls
