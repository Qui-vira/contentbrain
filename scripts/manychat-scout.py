"""Scout ManyChat UI to capture page structure."""
import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
OUT = os.path.join(os.path.dirname(__file__), "..")

async def scout():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        # Step 1: Go to login
        print("Loading login page...")
        await page.goto("https://manychat.com/login")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(OUT, "mc_01_login.png"))
        print("Screenshot: mc_01_login.png")

        # Dump all input elements
        inputs = await page.query_selector_all("input")
        print(f"\nFound {len(inputs)} input elements:")
        for inp in inputs:
            name = await inp.get_attribute("name")
            typ = await inp.get_attribute("type")
            placeholder = await inp.get_attribute("placeholder")
            cls = await inp.get_attribute("class")
            print(f"  name={name} type={typ} placeholder={placeholder}")

        # Dump buttons
        buttons = await page.query_selector_all("button")
        print(f"\nFound {len(buttons)} buttons:")
        for btn in buttons:
            text = await btn.inner_text()
            typ = await btn.get_attribute("type")
            print(f"  text='{text.strip()[:50]}' type={typ}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scout())
