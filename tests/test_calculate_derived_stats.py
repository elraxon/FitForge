import asyncio
import os
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Load the HTML content
        file_path = os.path.abspath("FitForgeV1.html")
        with open(file_path, "r") as f:
            html_content = f.read()

        await page.set_content(html_content, timeout=0)

        print("Testing calculateDerivedStats...")

        # Initialize player and test base stats
        await page.evaluate("""
            initializeNewGame();
            player.stats = { STR: 0, END: 0, AGI: 0, FOC: 0 };
            calculateDerivedStats();
        """)

        derived_stats = await page.evaluate("player.derivedStats")
        assert derived_stats['maxHp'] == 15
        assert derived_stats['maxStamina'] == 10
        assert derived_stats['maxMana'] == 10

        # Test with increased base stats
        await page.evaluate("""
            player.stats = { STR: 5, END: 5, AGI: 5, FOC: 5 };
            calculateDerivedStats();
        """)
        derived_stats = await page.evaluate("player.derivedStats")
        assert derived_stats['maxHp'] == 65
        assert derived_stats['maxStamina'] == 70
        assert derived_stats['maxMana'] == 65

        # Test with equipment
        await page.evaluate("""
            player.stats = { STR: 0, END: 0, AGI: 0, FOC: 0 };
            player.equipment.weapon = 'Wooden Stick';
            player.equipment.chest = 'Tattered Loincloth';
            calculateDerivedStats();
        """)
        derived_stats = await page.evaluate("player.derivedStats")
        assert derived_stats['maxHp'] == 25
        assert derived_stats['maxStamina'] == 15
        assert derived_stats['maxMana'] == 13

        # Test with skills
        await page.evaluate("""
            player.stats = { STR: 0, END: 0, AGI: 0, FOC: 0 };
            player.equipment = { weapon: null, chest: null, shield: null, helmet: null, gloves: null, boots: null, amulet: null };
            player.skills['Warriors Mettle'] = 1;
            calculateDerivedStats();
        """)
        derived_stats = await page.evaluate("player.derivedStats")
        assert derived_stats['maxHp'] == 21

        # Test capping current values
        await page.evaluate("""
            player.stats = { STR: 0, END: 0, AGI: 0, FOC: 0 };
            player.skills = {};
            calculateDerivedStats(); // max stats are 15, 10, 10
            player.derivedStats.currentHp = 100;
            player.derivedStats.currentStamina = 100;
            player.derivedStats.currentMana = 100;
            calculateDerivedStats();
        """)
        derived_stats = await page.evaluate("player.derivedStats")
        assert derived_stats['currentHp'] == 15
        assert derived_stats['currentStamina'] == 10
        assert derived_stats['currentMana'] == 10

        await browser.close()
        print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(run_test())
