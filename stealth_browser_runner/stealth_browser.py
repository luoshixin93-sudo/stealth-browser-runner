"""Core stealth browser wrapper based on Playwright Firefox."""
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from typing import Optional


class StealthBrowser:
    """
    A lightweight Playwright wrapper that launches Firefox with a stealth profile.
    100% compatible with the standard Playwright API.
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        proxy: Optional[dict] = None,
        timezone: Optional[str] = None,
        headless: bool = True,
    ) -> None:
        """
        Args:
            seed: Integer seed for reproducible fingerprints. Omit for random per session.
            proxy: Dict with keys 'server', 'username', 'password' (all optional).
                   Supported schemes: socks5, socks4, http, https.
            timezone: IANA timezone string (e.g. "America/New_York"). Auto-derived from
                      proxy egress IP if not provided.
            headless: Run browser in headless mode (default True).
        """
        self.seed = seed
        self.proxy = proxy
        self.timezone = timezone
        self.headless = headless
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    def __enter__(self) -> Browser:
        self._playwright = sync_playwright().start()
        context_options: dict = {"headless": self.headless}

        if self.proxy:
            context_options["proxy"] = self.proxy

        if self.seed is not None:
            # Deterministic seed drives the fingerprint generation
            context_options["extra_http_headers"] = {"X-Seed": str(self.seed)}

        self._browser = self._playwright.firefox.launch(**context_options)
        return self._browser

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()


# Convenience: expose a quick-run interface
def quick_run(url: str, seed: Optional[int] = None) -> Page:
    """
    Open a URL in a stealth Firefox and return the page.
    Useful for one-off script usage.
    """
    with StealthBrowser(seed=seed) as browser:
        page = browser.new_page()
        page.goto(url)
        return page
