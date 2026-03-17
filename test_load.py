import asyncio
import os
from playwright.async_api import async_playwright

async def run(playwright):
    browser = await playwright.chromium.launch()
    page = await browser.new_page()

    errors = []
    page.on("pageerror", lambda err: errors.append(err))

    with open("FitForgeV1.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    await page.set_content(html_content, timeout=0)

    # Check if the title is loaded properly
    title = await page.title()
    print(f"Page title: {title}")

    # Interact slightly to ensure nothing breaks (e.g. click "Forge My Hero" or enter name)
    # The initial screen requires name entry
    await page.fill("#playerNameInput", "TestHero")
    await page.click("text=Forge My Hero")

    # Check if main menu text is there
    content = await page.content()
    if "Main Menu - TestHero" in content:
        print("Main Menu reached successfully.")
    else:
        print("Failed to reach Main Menu.")

    await browser.close()

    if errors:
        print("JavaScript errors found:")
        for e in errors:
            print(e)
        raise Exception("JavaScript errors occurred")
    else:
        print("No JavaScript errors found.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == '__main__':
    asyncio.run(main())
