import re
from playwright.sync_api import sync_playwright

def test_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        with open("FitForgeV1.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        # Load content directly
        page.set_content(html_content, timeout=0)

        # Let it initialize
        page.wait_for_timeout(500)

        # Log in
        page.fill("#playerNameInput", "Test Player")
        page.click("button:has-text('Forge My Hero')")

        # Run onboarding bypass and save
        page.evaluate("unlockAllCoreStatsAndGrantGear()")
        page.evaluate("saveGame()")

        page.wait_for_timeout(200)

        # Check main menu displays the correct player name
        assert "Test Player" in page.text_content("h2")

        # Open character screen
        page.click("button:has-text('Character')")

        page.wait_for_timeout(200)

        # Ensure we are on character screen and stats are 1 (since unlockAllCoreStatsAndGrantGear sets them to 1)
        assert "Character - Test Player" in page.text_content("h2")

        # Open skills tab
        page.click("button:has-text('Skills')")
        page.wait_for_timeout(200)

        # Verify the Skills tab loaded classes
        skills_text = page.text_content("#mainContent")
        assert "Vanguard" in skills_text
        assert "Guardian" in skills_text
        assert "Striker" in skills_text
        assert "Arcanist" in skills_text
        assert "Power Strike" in skills_text

        browser.close()
