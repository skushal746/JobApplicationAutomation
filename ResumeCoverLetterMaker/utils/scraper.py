"""
utils/scraper.py

Scrapes the main text content from a job listing URL.
Uses Playwright for JavaScript rendering and BeautifulSoup for parsing.
"""

import logging
from bs4 import BeautifulSoup

# Tags whose content we skip entirely (navigation, scripts, ads, etc.)
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "svg"}

def scrape_job(url: str, timeout: int = 30000) -> str:
    """
    Fetch a job listing URL. Uses Selenium for Upwork, Playwright for others.
    """
    if "upwork.com" in url:
        return _scrape_selenium(url)
        
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logging.error("Playwright not installed. Falling back to basic requests.")
        return _scrape_fallback(url)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Navigate and wait for content
            print(f"  [Scraper] Navigating to {url}...")
            page.goto(url, wait_until="networkidle", timeout=timeout)
            
            # Extra wait for some JS-heavy sites
            page.wait_for_timeout(2000)
            
            html = page.content()
            browser.close()
            
            return _parse_html(html, url)
    except Exception as e:
        logging.error(f"Playwright scraping failed: {e}")
        return _scrape_fallback(url)

def _scrape_fallback(url: str) -> str:
    """Legacy requests-based scraper as fallback."""
    import requests
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return _parse_html(response.text, url)
    except Exception as e:
        raise Exception(f"All scraping methods failed for {url}: {e}")

def _scrape_selenium(url: str) -> str:
    """Use undetected-chromedriver for sites with heavy bot protection."""
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.support.ui import WebDriverWait
    except ImportError as ie:
        logging.error(f"undetected-chromedriver or selenium not installed: {ie}")
        return _scrape_fallback(url)
        
    options = uc.ChromeOptions()
    # Cloudflare often blocks headless=True even with undetected_chromedriver
    options.headless = False
    
    print(f"  [Scraper] Navigating to {url} via Selenium...")
    try:
        # Explicitly set version_main=147 to match your installed Chrome version
        driver = uc.Chrome(options=options, version_main=147)
        driver.get(url)
        
        # Simple wait to let Cloudflare and page load
        import time
        time.sleep(5)
        
        html = driver.page_source
        return _parse_html(html, url)
    except Exception as e:
        logging.error(f"Selenium scraping failed: {e}")
        return _scrape_fallback(url)
    finally:
        try:
            driver.quit()
        except:
            pass

def _parse_html(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Remove junk tags
    for tag in soup(SKIP_TAGS):
        tag.decompose()

    # Try known job-description containers
    content = _try_known_containers(soup)

    if not content:
        body = soup.find("body")
        content = body.get_text(separator="\n") if body else soup.get_text(separator="\n")

    cleaned = _clean_text(content)

    if len(cleaned) < 100:
        raise ValueError(f"Extracted text too short from {url}. Required JS might not have loaded.")

    return cleaned

def _try_known_containers(soup: BeautifulSoup) -> str:
    selectors = [
        "div.description__text", "div.show-more-less-html__markup", # LinkedIn
        "div#jobDescriptionText", # Indeed
        "div#content", "div.job-post-content", # Greenhouse
        "div.section-wrapper", # Lever
        "div[data-automation-id='jobPostingDescription']", # Workday
        "article", "main", "div.job-description"
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return el.get_text(separator="\n")
    return ""

def _clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join([l for l in lines if l])
