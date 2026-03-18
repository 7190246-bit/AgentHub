#!/usr/bin/env python3
"""
OpenClaw + Playwright 集成脚本
实现类似 gstack 的浏览器自动化功能
"""

import sys
import json
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Browser, Page
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright")
    sys.exit(1)


class OpenClawBrowser:
    """OpenClaw 浏览器自动化类"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None
        self.screenshots_dir = Path("~/.agenthub/screenshots").expanduser()
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def start(self):
        """启动浏览器"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        print(f"✅ 浏览器启动成功 (headless={self.headless})")
        return self

    def stop(self):
        """停止浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("🛑 浏览器已关闭")

    def goto(self, url: str, wait_until: str = "load"):
        """导航到 URL"""
        self.page.goto(url, wait_until=wait_until)
        print(f"📍 已导航到: {url}")
        return self

    def snapshot(self, name: str = None):
        """截图"""
        if name is None:
            name = f"snapshot_{int(time.time())}.png"
        path = self.screenshots_dir / name
        self.page.screenshot(path=str(path), full_page=True)
        print(f"📸 截图保存到: {path}")
        return str(path)

    def click(self, selector: str):
        """点击元素"""
        self.page.click(selector)
        print(f"👆 点击: {selector}")
        return self

    def type(self, selector: str, text: str, delay: int = 50):
        """输入文本"""
        self.page.type(selector, text, delay=delay)
        print(f"⌨️ 输入: {text} → {selector}")
        return self

    def evaluate(self, script: str):
        """执行 JavaScript"""
        result = self.page.evaluate(script)
        print(f"⚡ 执行脚本: {script[:50]}...")
        return result

    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        text = self.page.locator(selector).text_content()
        return text

    def get_attribute(self, selector: str, attr: str) -> str:
        """获取元素属性"""
        value = self.page.locator(selector).get_attribute(attr)
        return value

    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """等待元素出现"""
        self.page.wait_for_selector(selector, timeout=timeout)
        print(f"⏳ 等待元素: {selector}")
        return self

    def get_page_info(self) -> dict:
        """获取页面信息"""
        return {
            "url": self.page.url,
            "title": self.page.title(),
            "viewport": self.page.viewport_size,
        }


def main():
    """主函数 - 演示浏览器自动化"""
    print("=" * 50)
    print("🌐 OpenClaw + Playwright 浏览器自动化")
    print("=" * 50)

    # 启动浏览器
    browser = OpenClawBrowser(headless=False)
    browser.start()

    try:
        # 演示 1: 打开网页
        print("\n📌 示例 1: 打开网页")
        browser.goto("https://example.com")
        print(f"   标题: {browser.page.title()}")

        # 演示 2: 截图
        print("\n📌 示例 2: 截图")
        browser.snapshot("example.png")

        # 演示 3: 获取页面信息
        print("\n📌 示例 3: 页面信息")
        info = browser.get_page_info()
        print(f"   URL: {info['url']}")
        print(f"   Title: {info['title']}")

    finally:
        # 关闭浏览器
        browser.stop()

    print("\n✅ 演示完成！")


if __name__ == "__main__":
    main()
