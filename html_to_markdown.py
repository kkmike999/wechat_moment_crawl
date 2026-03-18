"""HTML 转 Markdown 工具"""

from markdownify import markdownify


def html_to_markdown(html: str) -> str:
    """
    将 HTML 内容转换为 Markdown 格式。

    Args:
        html: 输入的 HTML 字符串

    Returns:
        转换后的 Markdown 字符串
    """
    return markdownify(html)


if __name__ == "__main__":
    sample_html = "<h1>标题</h1><p>这是一段<strong>加粗</strong>文字。</p>"
    print(html_to_markdown(sample_html))
