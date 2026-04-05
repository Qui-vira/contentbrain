"""
Deploy ManyChat CLEARED Automation using existing Chrome session.
Bypasses Cloudflare by reusing your logged-in browser cookies.

IMPORTANT: Close Chrome completely before running this script.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "06-Drafts", "manychat", "cleared-config.json")
CHROME_USER_DATA = os.path.expanduser("~/AppData/Local/Temp/chrome-manychat")
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..")

with open(CONFIG_PATH) as f:
    config = json.load(f)


async def deploy():
    async with async_playwright() as p:
        # Launch using existing Chrome profile (has cookies/session)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_USER_DATA,
            channel="chrome",
            headless=False,
            slow_mo=800,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()

        # Navigate to ManyChat
        print("Step 1: Opening ManyChat...")
        await page.goto("https://manychat.com/", wait_until="domcontentloaded")
        await asyncio.sleep(5)

        ss = lambda name: page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"mc_{name}.png"))
        await ss("01_landing")

        # Check if we're logged in already
        url = page.url
        print(f"  Current URL: {url}")

        if "login" in url.lower():
            print("  Not logged in. Waiting for Cloudflare...")
            await asyncio.sleep(10)
            await ss("02_after_cf")
            url = page.url
            print(f"  URL after wait: {url}")

        # Navigate to automation page
        print("\nStep 2: Going to Automation...")
        await page.goto("https://manychat.com/fb122168305556613773/automation", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        await ss("03_automation")

        # Try direct IG automation URL patterns
        # ManyChat URL format: manychat.com/{page_id}/ig-automation or /automation
        current = page.url
        print(f"  URL: {current}")

        # Look for + New Automation button
        print("\nStep 3: Creating new automation...")
        try:
            new_btn = page.locator("button:has-text('New Automation'), button:has-text('Create'), a:has-text('New Automation'), [data-testid*='create'], [class*='create']")
            count = await new_btn.count()
            print(f"  Found {count} potential buttons")
            if count > 0:
                await new_btn.first.click()
                await asyncio.sleep(3)
                await ss("04_new_automation")
        except Exception as e:
            print(f"  Could not find button: {e}")
            await ss("04_error")

        # Look for Comment Trigger option
        print("\nStep 4: Selecting Instagram Comment trigger...")
        try:
            # Try clicking on comment-related elements
            triggers = page.locator("text=Comment, text=Instagram Comment, text=Comment Trigger, [data-testid*='comment']")
            count = await triggers.count()
            print(f"  Found {count} comment-related elements")
            if count > 0:
                for i in range(count):
                    text = await triggers.nth(i).inner_text()
                    print(f"    [{i}] {text.strip()[:60]}")
                await triggers.first.click()
                await asyncio.sleep(3)
                await ss("05_trigger")
        except Exception as e:
            print(f"  Trigger selection: {e}")
            await ss("05_error")

        # Set keyword
        print(f"\nStep 5: Setting keyword: {config['keyword']}")
        try:
            inputs = page.locator("input[type='text'], input[placeholder*='keyword' i], input[placeholder*='word' i]")
            count = await inputs.count()
            print(f"  Found {count} text inputs")
            for i in range(min(count, 5)):
                ph = await inputs.nth(i).get_attribute("placeholder") or ""
                val = await inputs.nth(i).input_value() or ""
                print(f"    [{i}] placeholder='{ph}' value='{val}'")
            await ss("06_keyword")
        except Exception as e:
            print(f"  Keyword: {e}")

        # Dump page content for debugging
        print("\nPage title:", await page.title())
        print("URL:", page.url)

        # Keep browser open so user can see/continue
        print("\n=== Browser is open. Check the screenshots and current state. ===")
        print("Press Ctrl+C to close when done.")

        try:
            await asyncio.sleep(300)  # Keep open 5 min
        except KeyboardInterrupt:
            pass

        await browser.close()


if __name__ == "__main__":
    asyncio.run(deploy())
