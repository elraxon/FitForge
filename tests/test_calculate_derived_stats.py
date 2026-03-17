import unittest
import os
from playwright.sync_api import sync_playwright

class TestCalculateDerivedStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        cls.page = cls.browser.new_page()

        # Load the HTML file content
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'FitForgeV1.html')
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        cls.page.set_content(html_content, timeout=0)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        # Reset player state before each test
        self.page.evaluate('initializeNewGame()')

    def test_derived_stats_calculation(self):
        # Set base stats and test derivation logic
        # Formulas:
        # maxHp = 15 + (END * 8) + (STR * 2)
        # maxStamina = 10 + (END * 5) + (AGI * 7)
        # maxMana = 10 + (FOC * 8) + (END * 3)
        self.page.evaluate('''() => {
            player.stats.STR = 5;
            player.stats.END = 3;
            player.stats.AGI = 4;
            player.stats.FOC = 2;
            // Clear equipment to ensure only base stats apply
            player.equipment = { weapon: null, chest: null, shield: null, helmet: null, gloves: null, boots: null, amulet: null };
            calculateDerivedStats();
        }''')

        player = self.page.evaluate('player')

        expected_max_hp = 15 + (3 * 8) + (5 * 2) # 15 + 24 + 10 = 49
        expected_max_stamina = 10 + (3 * 5) + (4 * 7) # 10 + 15 + 28 = 53
        expected_max_mana = 10 + (2 * 8) + (3 * 3) # 10 + 16 + 9 = 35

        self.assertEqual(player['derivedStats']['maxHp'], expected_max_hp)
        self.assertEqual(player['derivedStats']['maxStamina'], expected_max_stamina)
        self.assertEqual(player['derivedStats']['maxMana'], expected_max_mana)

    def test_current_stats_capped_at_max(self):
        # Ensure that if current stat is above max, calculateDerivedStats caps it
        self.page.evaluate('''() => {
            player.stats.STR = 1;
            player.stats.END = 1;
            player.stats.AGI = 1;
            player.stats.FOC = 1;
            player.equipment = { weapon: null, chest: null, shield: null, helmet: null, gloves: null, boots: null, amulet: null };

            // Set current above normal max
            player.derivedStats.currentHp = 999;
            player.derivedStats.currentStamina = 999;
            player.derivedStats.currentMana = 999;

            calculateDerivedStats();
        }''')

        player = self.page.evaluate('player')

        expected_max_hp = 15 + (1 * 8) + (1 * 2) # 25
        expected_max_stamina = 10 + (1 * 5) + (1 * 7) # 22
        expected_max_mana = 10 + (1 * 8) + (1 * 3) # 21

        self.assertEqual(player['derivedStats']['currentHp'], expected_max_hp)
        self.assertEqual(player['derivedStats']['currentStamina'], expected_max_stamina)
        self.assertEqual(player['derivedStats']['currentMana'], expected_max_mana)

    def test_current_stats_not_increased(self):
        # Ensure that if current stat is below max, calculateDerivedStats does NOT increase it
        self.page.evaluate('''() => {
            player.stats.STR = 5;
            player.stats.END = 5;
            player.stats.AGI = 5;
            player.stats.FOC = 5;
            player.equipment = { weapon: null, chest: null, shield: null, helmet: null, gloves: null, boots: null, amulet: null };
            calculateDerivedStats(); // calculate new max

            // Set current well below new max
            player.derivedStats.currentHp = 5;
            player.derivedStats.currentStamina = 5;
            player.derivedStats.currentMana = 5;

            calculateDerivedStats(); // run again
        }''')

        player = self.page.evaluate('player')

        self.assertEqual(player['derivedStats']['currentHp'], 5)
        self.assertEqual(player['derivedStats']['currentStamina'], 5)
        self.assertEqual(player['derivedStats']['currentMana'], 5)

    def test_null_player(self):
        # Should gracefully return and not throw errors
        self.page.evaluate('player = null; calculateDerivedStats();')
        player = self.page.evaluate('player')
        self.assertIsNone(player)

if __name__ == '__main__':
    unittest.main()
