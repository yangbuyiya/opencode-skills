"""
Playwright 渲染工具模块
提供统一的 Playwright 生命周期管理和公共渲染助手
"""

from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, PlaywrightContextManager


class RenderSession:
    """
    Playwright 渲染会话管理器
    封装浏览器和页面的生命周期，支持复用以减少启动开销
    """

    def __init__(
        self,
        width: int = 1080,
        height: int = 1440,
        headless: bool = True
    ):
        self.width = width
        self.height = height
        self.headless = headless
        self._playwright: Optional[PlaywrightContextManager] = None
        self._playwright_obj = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        self._playwright = async_playwright()
        self._playwright_obj = await self._playwright.__aenter__()
        self.browser = await self._playwright_obj.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page(
            viewport={'width': self.width, 'height': self.height}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self._playwright_obj:
            await self._playwright.__aexit__(exc_type, exc_val, exc_tb)

    async def prepare_page(self, width: Optional[int] = None, height: Optional[int] = None):
        """
        准备页面状态，重置 viewport 和滚动位置
        用于在复用页面时避免状态污染
        """
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        await self.page.set_viewport_size({'width': width, 'height': height})
        await self.page.evaluate("""
            () => {
                window.scrollTo(0, 0);
                try {
                    localStorage.clear();
                } catch (e) {}
                try {
                    sessionStorage.clear();
                } catch (e) {}
            }
        """)


async def ensure_fonts_ready(page: Page, timeout: int = 5000):
    """
    等待字体加载完成
    避免截到未替换的回退字体
    """
    try:
        await page.evaluate("""
            async () => {
                if (document.fonts && document.fonts.ready) {
                    await document.fonts.ready;
                }
            }
        """)
    except Exception:
        pass
    
    await page.wait_for_timeout(100)


async def ensure_content_ready(page: Page):
    """
    等待内容就绪：网络空闲 + 字体加载完成
    """
    await page.wait_for_load_state('networkidle', timeout=10000)
    await ensure_fonts_ready(page)


async def screenshot_card(
    page: Page,
    html_content: str,
    output_path: str,
    width: int = 1080,
    height: int = 1440,
    clip_x: int = 0,
    clip_y: int = 0
):
    """
    统一的卡片截图函数
    封装了设置内容、等待就绪、截图的完整流程
    """
    await page.set_viewport_size({'width': width, 'height': height})
    await page.set_content(html_content, wait_until='networkidle')
    await ensure_content_ready(page)
    
    await page.screenshot(
        path=output_path,
        clip={'x': clip_x, 'y': clip_y, 'width': width, 'height': height},
        type='png'
    )


async def measure_content_height(page: Page, html_content: str) -> int:
    """
    使用 Playwright 测量实际内容高度
    """
    await page.set_content(html_content, wait_until='networkidle')
    await ensure_fonts_ready(page)
    
    height = await page.evaluate('''() => {
        const inner = document.querySelector('.card-inner');
        if (inner) {
            return inner.scrollHeight;
        }
        const container = document.querySelector('.card-container');
        return container ? container.scrollHeight : document.body.scrollHeight;
    }''')
    
    return height
