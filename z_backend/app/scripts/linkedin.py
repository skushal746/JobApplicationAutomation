import asyncio
from playwright.async_api import async_playwright, Page
from typing import Callable, Awaitable, Dict, Optional
from .base import BaseAutomation

class LinkedInStrategy(BaseAutomation):
    async def run(
        self, 
        job_id: int,
        get_answer: Callable[[str], Awaitable[str]],
        credentials: Optional[Dict[str, str]] = None,
        resumes: Optional[list] = None
    ) -> bool:
        # Note: job_url is not in the model anymore, 
        # but the script needs a place to start. 
        # For now, we expect the caller to have handled the initial navigation or provide the URL.
        # In this refactor, I'll assume we need to be passed the job_url somehow.
        # Let's adjust the run signature to include job_url as well.
        pass

    async def execute(
        self,
        job_url: str,
        company_id: int,
        get_answer: Callable[[str], Awaitable[str]]
    ) -> bool:
        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(self.browser_url)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(job_url, wait_until="networkidle")

                easy_apply_button = page.locator("button:has-text('Easy Apply')").first
                if await easy_apply_button.count() == 0:
                    return False

                await easy_apply_button.click()
                await asyncio.sleep(2)

                for _ in range(10):
                    await self._handle_form(page, get_answer)
                    next_button = page.locator("button:has-text('Next'), button:has-text('Review'), button:has-text('Submit application')").first
                    if await next_button.count() == 0: break
                    
                    text = await next_button.inner_text()
                    await next_button.click()
                    await asyncio.sleep(1)
                    if "Submit application" in text:
                        await browser.close()
                        return True

                await browser.close()
                return False
            except Exception as e:
                print(f"LinkedIn Error: {e}")
                return False

    async def _handle_form(self, page: Page, get_answer: Callable[[str], Awaitable[str]]):
        questions = page.locator(".jobs-easy-apply-form-section__grouping")
        for i in range(await questions.count()):
            section = questions.nth(i)
            label = section.locator("label").first
            if await label.count() == 0: continue
            q_text = (await label.inner_text()).strip()
            
            # Use the callback to get the answer (handles DB + LLM)
            answer = await get_answer(q_text)
            
            input_field = section.locator("input[type='text'], textarea, select").first
            if await input_field.count() > 0:
                if await input_field.evaluate("el => el.tagName") == "SELECT":
                    await input_field.select_option(label=answer)
                else:
                    await input_field.fill(answer)
