import unittest
import os
from playwright.sync_api import sync_playwright

class TestUpgradeStat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        with open('FitForgeV1.html', 'r', encoding='utf-8') as f:
            cls.html_content = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.set_content(self.html_content, timeout=0)

        # Setup initial state
        self.page.evaluate('''() => {
            player.playerName = "TestPlayer";
            player.onboarding.nameSet = true;
            changeState('mainMenu');
        }''')

    def tearDown(self):
        self.context.close()

    def test_upgrade_stat_cannot_level_yet(self):
        self.page.evaluate('''() => {
            player.stats.STR = 5;
            player.gp = 1000;
            upgradeStat('STR');
        }''')

        str_level = self.page.evaluate('player.stats.STR')
        gp = self.page.evaluate('player.gp')

        self.assertEqual(str_level, 5)
        self.assertEqual(gp, 1000)

        last_log = self.page.evaluate('document.querySelector("#gameLogContainer p").textContent')
        self.assertTrue("not yet upgradeable" in last_log)

    def test_upgrade_stat_max_level(self):
        self.page.evaluate('''() => {
            unlockAllCoreStatsAndGrantGear();
            player.stats.STR = 25;
            player.gp = 100000;
            upgradeStat('STR');
        }''')

        str_level = self.page.evaluate('player.stats.STR')
        self.assertEqual(str_level, 25)

        last_log = self.page.evaluate('document.querySelector("#gameLogContainer p").textContent')
        self.assertTrue("already at max level" in last_log)

    def test_upgrade_stat_not_enough_gp(self):
        self.page.evaluate('''() => {
            unlockAllCoreStatsAndGrantGear();
            player.stats.STR = 5;
            player.gp = 0;
            upgradeStat('STR');
        }''')

        str_level = self.page.evaluate('player.stats.STR')
        self.assertEqual(str_level, 5)

        last_log = self.page.evaluate('document.querySelector("#gameLogContainer p").textContent')
        self.assertTrue("Not enough GP" in last_log)

    def test_upgrade_stat_success(self):
        self.page.evaluate('''() => {
            unlockAllCoreStatsAndGrantGear();
            player.stats.STR = 5;
            player.gp = 100;
            player.derivedStats.currentHp = 1;
            upgradeStat('STR');
        }''')

        str_level = self.page.evaluate('player.stats.STR')
        gp = self.page.evaluate('player.gp')

        # 15 * (1.25^5) = 45.776 -> round -> 46
        cost = 46

        self.assertEqual(str_level, 6)
        self.assertEqual(gp, 100 - cost)

        last_logs = self.page.evaluate('''() => {
            return Array.from(document.querySelectorAll("#gameLogContainer p")).map(p => p.textContent);
        }''')

        found = False
        for log in last_logs:
            if "upgraded to Level 6" in log:
                found = True
                break
        self.assertTrue(found, f"Expected success log not found in {last_logs}")

        current_hp = self.page.evaluate('player.derivedStats.currentHp')
        max_hp = self.page.evaluate('player.derivedStats.maxHp')
        self.assertEqual(current_hp, max_hp)
        self.assertTrue(current_hp > 1)

if __name__ == '__main__':
    unittest.main()
