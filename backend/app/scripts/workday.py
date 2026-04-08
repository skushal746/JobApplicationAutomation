import asyncio
from playwright.async_api import async_playwright, Page
from typing import Callable, Awaitable, Dict, Optional, List
from .base import BaseAutomation

class WorkdayStrategy(BaseAutomation):
    async def run(self, *args, **kwargs):
        # Implementation in execute for more explicit arg naming
        pass

    async def execute(
        self,
        job_url: str,
        company_id: int,
        get_answer: Callable[[str], Awaitable[str]],
        credentials: Dict[str, str],
        resume_locations: List[str]
    ) -> bool:
        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(self.browser_url)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(job_url, wait_until="networkidle")

                # 1. Start Application - Apply Manually
                apply_button = page.locator("button:has-text('Apply')").first
                await apply_button.click()
                await page.locator("button:has-text('Apply Manually')").click()
                await asyncio.sleep(2)

                # 2. Login if needed
                if "login" in page.url.lower():
                    # Handle specific login fields based on Workday's standard
                    await page.fill("input[type='email'], input[name='username']", credentials.get("username", ""))
                    await page.fill("input[type='password']", credentials.get("password", ""))
                    await page.click("button[type='submit'], button:has-text('Sign In')")
                    await asyncio.sleep(3)

                # 3. Form Loop
                max_steps = 8
                for _ in range(max_steps):
                    await self._fill_workday_section(page, get_answer)
                    
                    # Upload Logic
                    if "resume" in page.url.lower() or await page.locator("input[type='file']").count() > 0:
                        file_input = page.locator("input[type='file']").first
                        if await file_input.count() > 0 and resume_locations:
                            await file_input.set_input_files(resume_locations[0])

                    next_btn = page.locator("button:has-text('Save and Continue'), button:has-text('Submit')").first
                    if await next_btn.count() == 0: break
                    
                    btn_text = await next_btn.inner_text()
                    await next_btn.click()
                    await asyncio.sleep(2)
                    
                    if "Submit" in btn_text:
                        await browser.close()
                        return True

                await browser.close()
                return False
            except Exception as e:
                print(f"Workday Error: {e}")
                return False

    async def _fill_workday_section(self, page: Page, get_answer: Callable[[str], Awaitable[str]]):
        labels = page.locator("label")
        for i in range(await labels.count()):
            label = labels.nth(i)
            q_text = (await label.inner_text()).strip()
            if not q_text: continue
            
            answer = await get_answer(q_text)
            
            # Find associated input by id or aria-labelledby
            input_id = await label.get_attribute("for")
            if input_id:
                input_field = page.locator(f"#{input_id.replace('.', '\\.')}")
                if await input_field.count() > 0:
                    tag = await input_field.evaluate("el => el.tagName")
                    if tag == "SELECT":
                        await input_field.select_option(label=answer)
                    else:
                        await input_field.fill(answer)
