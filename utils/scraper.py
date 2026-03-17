"""
src/scraper.py

Scrapes the main text content from a job listing URL.
Handles common job boards (LinkedIn, Indeed, Greenhouse, Lever, etc.)
by extracting all visible text and stripping boilerplate.
"""

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Tags whose content we skip entirely (navigation, scripts, ads, etc.)
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "svg"}


def scrape_job(url: str, timeout: int = 15) -> str:
    """
    Fetch a job listing URL and return the main readable text.

    Args:
        url:     Full URL to the job listing page.
        timeout: HTTP request timeout in seconds.

    Returns:
        Extracted visible text of the job description.

    Raises:
        requests.HTTPError: If the server returns a non-2xx response.
        ValueError:         If no meaningful text could be extracted.
    """
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Remove junk tags in-place
    for tag in soup(SKIP_TAGS):
        tag.decompose()

    # Try known job-description containers first
    content = _try_known_containers(soup)

    # Fall back to full body text
    if not content:
        body = soup.find("body")
        content = body.get_text(separator="\n") if body else soup.get_text(separator="\n")

    cleaned = _clean_text(content)

    if len(cleaned) < 100:
        raise ValueError(
            f"Could not extract meaningful text from URL: {url}\n"
            "The page may require JavaScript or a login. "
            "Try copying the job description directly."
        )

    return cleaned


def _try_known_containers(soup: BeautifulSoup) -> str:
    """Try CSS selectors / IDs common across major job boards."""
    selectors = [
        # LinkedIn
        "div.description__text",
        "div.show-more-less-html__markup",
        # Indeed
        "div#jobDescriptionText",
        # Greenhouse
        "div#content",
        "div.job-post-content",
        # Lever
        "div.section-wrapper",
        # Workday
        "div[data-automation-id='jobPostingDescription']",
        # Generic
        "article",
        "main",
        "div.job-description",
        "div.jobDescription",
        "div#job-description",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return el.get_text(separator="\n")
    return ""


def _clean_text(text: str) -> str:
    """Collapse excessive whitespace/blank lines."""
    lines = [line.strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    return "\n".join(non_empty)
