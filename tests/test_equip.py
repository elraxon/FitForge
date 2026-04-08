import pytest
from playwright.sync_api import Page

def test_equip_missing_item(page: Page):
    # Load the game
    with open("FitForgeV1.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    page.set_content(html_content)

    # Bypass the tutorial and get to a state where we can equip
    page.evaluate("unlockAllCoreStatsAndGrantGear()")
    page.evaluate("player.playerName = 'TestPlayer'")
    page.evaluate("player.onboarding.nameSet = true")

    # Store the initial state
    initial_equipment = page.evaluate("player.equipment")

    # Listen to console errors (this is where the error log goes)
    errors = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

    # Attempt to equip a non-existent item
    page.evaluate("equipItem('NonExistentItem123')")

    # Verify the equipment state hasn't changed
    final_equipment = page.evaluate("player.equipment")
    assert initial_equipment == final_equipment, "Equipment state should not change when equipping a missing item"

    # Verify the error was logged
    assert any("[EQUIP FAIL] Item data not found for: NonExistentItem123" in err for err in errors), "Error message should be logged to console"

    # Verify the error was added to the game log (using DOM)
    log_texts = page.evaluate("Array.from(document.querySelectorAll('.game-log-container p.error')).map(p => p.textContent)")
    assert any("Error: Item data for 'NonExistentItem123' not found. Cannot equip." in log for log in log_texts), "Error should be added to the game log"
