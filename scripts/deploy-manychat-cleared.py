"""
Deploy ManyChat CLEARED DM Automation via Playwright
Trigger: Comment "CLEARED" on SEC 16 Tokens carousel
"""
import asyncio
import json
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

EMAIL = os.getenv("MANYCHAT_EMAIL")
PASSWORD = os.getenv("MANYCHAT_PASSWORD")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "06-Drafts", "manychat", "cleared-config.json")

with open(CONFIG_PATH) as f:
    config = json.load(f)

KEYWORD = config["keyword"]
COMMENT_REPLIES = config["comment_replies"]
OPENING_DM = config["opening_dm"]
DELIVERY_DM = config["delivery_dm"]
FOLLOW_UP_DM = config["follow_up_dm"]
LINK_URL = config["link_url"]


async def deploy():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        # Step 1: Login
        print("Step 1: Logging into ManyChat...")
        await page.goto("https://manychat.com/login")
        await page.wait_for_load_state("networkidle")

        await page.fill('input[name="email"], input[type="email"]', EMAIL)
        await page.fill('input[name="password"], input[type="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        print("  Logged in.")

        # Step 2: Navigate to Automation
        print("Step 2: Navigating to Automation...")
        try:
            await page.click('text=Automation', timeout=10000)
        except Exception:
            try:
                await page.click('[data-testid="automation"], a[href*="automation"]', timeout=5000)
            except Exception:
                print("  Could not find Automation tab. Taking screenshot...")
                await page.screenshot(path="manychat_nav.png")

        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # Step 3: Create new Comment Automation
        print("Step 3: Creating new Comment Automation...")
        try:
            new_btn = page.locator('button:has-text("New"), button:has-text("Create"), a:has-text("New Automation")')
            await new_btn.first.click(timeout=10000)
            await asyncio.sleep(2)
        except Exception:
            print("  Could not find New Automation button. Taking screenshot...")
            await page.screenshot(path="manychat_automation.png")

        # Step 4: Select Comment trigger type
        print("Step 4: Selecting Instagram Comment trigger...")
        try:
            await page.click('text=Comment', timeout=10000)
            await asyncio.sleep(1)
            await page.click('text=Instagram Comment', timeout=5000)
            await asyncio.sleep(2)
        except Exception:
            print("  Looking for comment trigger...")
            await page.screenshot(path="manychat_trigger.png")

        # Step 5: Set keyword
        print(f"Step 5: Setting keyword: {KEYWORD}")
        try:
            keyword_input = page.locator('input[placeholder*="keyword"], input[placeholder*="Keyword"], input[name*="keyword"]')
            await keyword_input.fill(KEYWORD)
            await asyncio.sleep(1)
        except Exception:
            print("  Could not find keyword input. Taking screenshot...")
            await page.screenshot(path="manychat_keyword.png")

        # Step 6: Set comment replies
        print("Step 6: Setting comment replies...")
        try:
            for i, reply in enumerate(COMMENT_REPLIES[:3]):
                reply_input = page.locator('textarea, input[placeholder*="reply"], input[placeholder*="Reply"]').nth(i)
                await reply_input.fill(reply)
                await asyncio.sleep(0.5)
                if i < 2:
                    try:
                        add_btn = page.locator('button:has-text("Add Reply"), button:has-text("Add Variation"), button:has-text("Add")')
                        await add_btn.first.click(timeout=3000)
                    except Exception:
                        pass
        except Exception:
            print("  Setting replies via available fields...")
            await page.screenshot(path="manychat_replies.png")

        # Step 7: Set DM messages
        print("Step 7: Setting DM flow...")
        try:
            dm_area = page.locator('textarea').first
            await dm_area.fill(f"{OPENING_DM}\n\n{DELIVERY_DM}")
            await asyncio.sleep(1)
        except Exception:
            print("  Could not set DM messages. Taking screenshot...")
            await page.screenshot(path="manychat_dm.png")

        # Step 8: Save/Activate
        print("Step 8: Saving automation...")
        try:
            save_btn = page.locator('button:has-text("Save"), button:has-text("Publish"), button:has-text("Activate")')
            await save_btn.first.click(timeout=10000)
            await asyncio.sleep(3)
            print("  Automation saved!")
        except Exception:
            print("  Could not find save button. Taking screenshot...")
            await page.screenshot(path="manychat_save.png")

        # Take final screenshot
        ss_path = os.path.join(os.path.dirname(__file__), "..", "manychat_final.png")
        await page.screenshot(path=ss_path)
        print(f"  Final screenshot: {ss_path}")

        await asyncio.sleep(2)
        await browser.close()

    print(f"\nDone! CLEARED automation deployment complete.")
    print(f"Keyword: {KEYWORD}")
    print(f"PDF Link: {LINK_URL}")
    print("Check screenshots if any steps need manual adjustment in ManyChat UI.")


if __name__ == "__main__":
    asyncio.run(deploy())
