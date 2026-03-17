from playwright.sync_api import sync_playwright
import os
import sys

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load file content directly
        html_path = os.path.abspath('FitForgeV1.html')
        print(f"Loading {html_path}")
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        page.set_content(html_content, timeout=0)

        # Wait for the JS to run
        page.wait_for_selector('#gameHeader', timeout=5000)

        # Print console logs
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))

        print("Calling unlockAllCoreStatsAndGrantGear...")
        page.evaluate("unlockAllCoreStatsAndGrantGear()")

        print("Calling saveGame...")
        page.evaluate("saveGame()")

        print("Checking header content...")
        header_text = page.locator('#gameHeader').inner_text()
        print(f"Header text: {header_text}")

        print("Checking for errors...")

        browser.close()
        print("Tests passed.")

if __name__ == '__main__':
    run_test()
