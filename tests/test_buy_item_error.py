import pytest
from playwright.sync_api import sync_playwright

def test_buy_item_error_paths():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local HTML file
        with open("FitForgeV1.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        page.set_content(html_content, timeout=0)

        # Bypass tutorial and set up game state
        page.evaluate("""() => {
            initializeNewGame();
            player.playerName = 'TestHero';
            player.onboarding.nameSet = true;
            unlockAllCoreStatsAndGrantGear();
            player.gp = 100; // give some starting GP
            saveGame();
        }""")

        initial_gp = page.evaluate("player.gp")
        initial_inventory_length = page.evaluate("player.inventory.length")

        # Test Case 1: Invalid item name
        page.evaluate("buyItem('NonExistentItem')")

        assert page.evaluate("player.gp") == initial_gp
        assert page.evaluate("player.inventory.length") == initial_inventory_length

        log_texts = page.locator("#gameLogContainer p").all_inner_texts()
        assert any("Item NonExistentItem not found in shop." in text for text in log_texts)
        assert page.locator("#gameLogContainer p.error").first.inner_text() == "Item NonExistentItem not found in shop."

        # Test Case 2: Valid item but 0 GP (e.g. Wooden Stick has gp: 0)
        page.evaluate("buyItem('Wooden Stick')")

        # Verify state hasn't changed
        assert page.evaluate("player.gp") == initial_gp
        assert page.evaluate("player.inventory.length") == initial_inventory_length

        # Verify correct error log
        log_texts = page.locator("#gameLogContainer p").all_inner_texts()
        assert any("Item Wooden Stick is not available for purchase." in text for text in log_texts)
        assert page.locator("#gameLogContainer p.error").first.inner_text() == "Item Wooden Stick is not available for purchase."

        # Test Case 3: Valid item, but undefined GP
        page.evaluate("""() => {
            EQUIPMENT_DATA['Broken Sword'] = { name: "Broken Sword", type: "Weapon", tier: 1 }; // no gp property
            buyItem('Broken Sword');
        }""")

        # Verify state hasn't changed
        assert page.evaluate("player.gp") == initial_gp
        assert page.evaluate("player.inventory.length") == initial_inventory_length

        # Verify correct error log
        log_texts = page.locator("#gameLogContainer p").all_inner_texts()
        assert any("Item Broken Sword is not available for purchase." in text for text in log_texts)
        assert page.locator("#gameLogContainer p.error").first.inner_text() == "Item Broken Sword is not available for purchase."

        browser.close()

if __name__ == "__main__":
    test_buy_item_error_paths()
