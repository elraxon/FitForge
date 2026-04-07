from playwright.sync_api import sync_playwright
import os

def test_potions():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the HTML content
        with open("FitForgeV1.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        page.set_content(html_content, timeout=0)

        page.evaluate("""
            player.playerName = "TestPlayer";
            initializeNewGame();
            unlockAllCoreStatsAndGrantGear();

            // Wait, maybe saveGame or updateDisplay inside usePotionOutsideCombat
            // is resetting currentHp back to something?
            // Let's stub them out to isolate applyPotionEffect testing
            window.saveGame = function() {};
            window.updateDisplay = function() {};
            window.renderCombatScreen = function() {};
            window.updateDerivedStats = function() {};

            player.inventory.push("Minor Health Potion");
            player.inventory.push("Minor Stamina Potion");
            player.inventory.push("Minor Mana Potion");

            player.derivedStats.maxHp = 100;
            player.derivedStats.currentHp = 50;

            player.derivedStats.maxStamina = 100;
            player.derivedStats.currentStamina = 50;

            player.derivedStats.maxMana = 100;
            player.derivedStats.currentMana = 50;
        """)

        # Test usePotionOutsideCombat
        page.evaluate("""
            usePotionOutsideCombat("Minor Health Potion");
        """)

        hp = page.evaluate("player.derivedStats.currentHp")
        print(f"HP after Minor Health Potion: {hp}")
        assert hp > 50, f"HP should have increased, was {hp}"

        page.evaluate("""
            usePotionOutsideCombat("Minor Stamina Potion");
        """)

        stamina = page.evaluate("player.derivedStats.currentStamina")
        print(f"Stamina after Minor Stamina Potion: {stamina}")
        assert stamina > 50, f"Stamina should have increased, was {stamina}"

        page.evaluate("""
            usePotionOutsideCombat("Minor Mana Potion");
        """)

        mana = page.evaluate("player.derivedStats.currentMana")
        print(f"Mana after Minor Mana Potion: {mana}")
        assert mana > 50, f"Mana should have increased, was {mana}"

        # Test playerUsePotionInCombat
        page.evaluate("""
            player.inventory.push("Minor Health Potion");
            player.derivedStats.currentHp = 50;
            combatState.active = true;
            combatState.playerTurn = true;
            playerUsePotionInCombat("Minor Health Potion");
        """)

        hp2 = page.evaluate("player.derivedStats.currentHp")
        print(f"HP after combat potion: {hp2}")
        assert hp2 > 50, f"HP should have increased in combat, was {hp2}"

        print("All tests passed!")
        browser.close()

if __name__ == "__main__":
    test_potions()
