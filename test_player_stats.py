import unittest
from playwright.sync_api import sync_playwright

class TestPlayerStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        with open("FitForgeV1.html", "r", encoding="utf-8") as f:
            cls.html = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.page.set_content(self.html, timeout=0)

    def tearDown(self):
        self.page.close()

    def test_getPlayerTotalStat_null_player(self):
        # When player is null, should return 0
        res = self.page.evaluate('''() => {
            player = null;
            return getPlayerTotalStat("STR");
        }''')
        self.assertEqual(res, 0)

    def test_getPlayerTotalStat_null_stats(self):
        # When player.stats is missing or null, should return 0
        res = self.page.evaluate('''() => {
            player = { stats: null };
            return getPlayerTotalStat("STR");
        }''')
        self.assertEqual(res, 0)

    def test_getPlayerTotalStat_missing_stat_in_player(self):
        # When stats is defined, but the specific stat is missing, should default to 0 base
        res = self.page.evaluate('''() => {
            player = { stats: { "END": 10 }, equipment: {}, skills: {} };
            return getPlayerTotalStat("STR");
        }''')
        self.assertEqual(res, 0)

    def test_getPlayerTotalStat_base_stat_only(self):
        # Tests the base stat mapping logic
        res = self.page.evaluate('''() => {
            player = {
                stats: { "STR": 10 },
                equipment: {},
                skills: {}
            };
            return getPlayerTotalStat("STR");
        }''')
        self.assertEqual(res, 10)

    def test_getPlayerTotalStat_with_equipment(self):
        # Tests equipment bonuses mapping logic
        res = self.page.evaluate('''() => {
            player = {
                stats: { "STR": 10 },
                equipment: { "weapon": "TestWeapon", "armor": "TestArmor" },
                skills: {}
            };
            EQUIPMENT_DATA["TestWeapon"] = { str: 5 };
            EQUIPMENT_DATA["TestArmor"] = { str: 2 };
            return getPlayerTotalStat("STR");
        }''')
        self.assertEqual(res, 17) # 10 (base) + 5 (weapon) + 2 (armor)

    def test_getPlayerTotalStat_str_with_skill(self):
        # Tests STR mapping with Warriors Mettle skill
        res = self.page.evaluate('''() => {
            player = {
                stats: { "STR": 10 },
                equipment: {},
                skills: { "Warriors Mettle": 2 }
            };
            SKILL_DATA["Warriors Mettle"] = {
                levels: [
                    { strBonus: 2 }, // level 1
                    { strBonus: 4 }  // level 2
                ]
            };
            return getPlayerTotalStat("STR");
        }''')
        self.assertEqual(res, 14) # 10 (base) + 4 (level 2)

    def test_getPlayerTotalStat_end_with_skill(self):
        # Tests END mapping with Reinforced Vitality skill
        res = self.page.evaluate('''() => {
            player = {
                stats: { "END": 5 },
                equipment: {},
                skills: { "Reinforced Vitality": 1 }
            };
            SKILL_DATA["Reinforced Vitality"] = {
                levels: [
                    { endBonus: 3 } // level 1
                ]
            };
            return getPlayerTotalStat("END");
        }''')
        self.assertEqual(res, 8) # 5 (base) + 3 (level 1)

    def test_getPlayerTotalStat_agi_with_skill(self):
        # Tests AGI mapping with Fleet Footed skill
        res = self.page.evaluate('''() => {
            player = {
                stats: { "AGI": 12 },
                equipment: {},
                skills: { "Fleet Footed": 3 }
            };
            SKILL_DATA["Fleet Footed"] = {
                levels: [
                    { agiBonus: 1 }, // level 1
                    { agiBonus: 2 }, // level 2
                    { agiBonus: 5 }  // level 3
                ]
            };
            return getPlayerTotalStat("AGI");
        }''')
        self.assertEqual(res, 17) # 12 (base) + 5 (level 3)

    def test_getPlayerTotalStat_foc_with_skill(self):
        # Tests FOC mapping with Inner Sight skill
        res = self.page.evaluate('''() => {
            player = {
                stats: { "FOC": 8 },
                equipment: {},
                skills: { "Inner Sight": 1 }
            };
            SKILL_DATA["Inner Sight"] = {
                levels: [
                    { focBonus: 2 } // level 1
                ]
            };
            return getPlayerTotalStat("FOC");
        }''')
        self.assertEqual(res, 10) # 8 (base) + 2 (level 1)

    def test_getPlayerTotalStat_adrenaline_surge_buff(self):
        # Verifies adrenaline surge buff logic does not break anything even when commented out in implementation
        res = self.page.evaluate('''() => {
            player = {
                stats: { "STR": 10 },
                equipment: {},
                skills: {}
            };
            combatState = {
                playerStatusEffects: [
                    { name: "Adrenaline Surge Buff", strBonus: 5 }
                ]
            };
            return getPlayerTotalStat("STR");
        }''')
        # Expect 10 since the bonus addition `// skillBonus += surgeEffect.strBonus;` is commented out.
        self.assertEqual(res, 10)

    def test_getPlayerTotalStat_all_combined(self):
        # Tests the combination of base stat + equipment + skill bonus
        res = self.page.evaluate('''() => {
            player = {
                stats: { "STR": 10 },
                equipment: { "weapon": "AwesomeSword" },
                skills: { "Warriors Mettle": 1 }
            };
            EQUIPMENT_DATA["AwesomeSword"] = { str: 5 };
            SKILL_DATA["Warriors Mettle"] = {
                levels: [
                    { strBonus: 3 } // level 1
                ]
            };
            return getPlayerTotalStat("STR");
        }''')
        self.assertEqual(res, 18) # 10 (base) + 5 (equip) + 3 (skill)

if __name__ == '__main__':
    unittest.main()
