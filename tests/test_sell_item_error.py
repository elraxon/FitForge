import os
from playwright.sync_api import sync_playwright

def test_sell_item_not_in_inventory():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Read the file content
        with open("FitForgeV1.html", "r") as f:
            html_content = f.read()

        # Set content directly, no wait
        page.set_content(html_content, timeout=0)

        # Give it a tiny bit of time to settle if needed, or just proceed
        # Since we are just calling JS functions, we might not need to wait for everything.

        # Initialize player state: empty inventory and 0 GP
        page.evaluate('''() => {
            if (typeof initializeNewGame === 'undefined') {
                 // If not yet loaded, wait a bit or try to find it
                 return;
            }
            initializeNewGame();
            player.inventory = [];
            player.gp = 0;
            updateDisplay();
        }''')

        # Call sellItem with 'Rusty Dagger' which is not in inventory
        page.evaluate("sellItem('Rusty Dagger')")

        # Check if the error message is in the log
        log_container = page.locator("#gameLogContainer")
        log_text = log_container.inner_text()

        expected_error = "Item Rusty Dagger not found in your inventory to sell."
        assert expected_error in log_text, f"Expected error message '{expected_error}' not found in log: {log_text}"

        # Check if GP remains 0
        player_gp = page.evaluate("player.gp")
        assert player_gp == 0, f"Expected player GP to be 0, but got {player_gp}"

        print("Test passed: Missing error path for sellItem correctly handles item not in inventory.")
        browser.close()

if __name__ == "__main__":
    try:
        test_sell_item_not_in_inventory()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
