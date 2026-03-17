from playwright.sync_api import sync_playwright

def test_get_player_total_stat():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Read the HTML content directly
        with open("FitForgeV1.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        # Load content with no timeout
        page.set_content(html_content, timeout=0)

        # Ensure page is ready
        page.wait_for_selector("#gameHeader")

        # Unlock basic game state
        page.evaluate("unlockAllCoreStatsAndGrantGear()")

        # Test case 1: player or player.stats is missing
        # Temporarily nullify player
        res_null = page.evaluate('''() => {
            const originalPlayer = player;
            player = null;
            const res = getPlayerTotalStat('STR');
            player = originalPlayer;
            return res;
        }''')
        assert res_null == 0, f"Expected 0 when player is null, got {res_null}"

        # Test case 2: Base stat only (no equipment, no skills)
        page.evaluate('''() => {
            player.stats.STR = 5;
            player.equipment.weapon = null;
            player.equipment.chest = null;
            player.skills = {};
        }''')
        res_base = page.evaluate("getPlayerTotalStat('STR')")
        assert res_base == 5, f"Expected base STR 5, got {res_base}"

        # Test case 3: Base stat + Equipment bonus
        # "Short Sword" gives +2 STR
        page.evaluate('''() => {
            player.equipment.weapon = "Short Sword";
        }''')
        res_equip = page.evaluate("getPlayerTotalStat('STR')")
        assert res_equip == 7, f"Expected base(5) + equip(2) = 7, got {res_equip}"

        # Test case 4: Base stat + Equipment + Skill bonus (STR)
        # "Warriors Mettle" level 1 gives +3 STR
        page.evaluate('''() => {
            player.skills["Warriors Mettle"] = 1;
        }''')
        res_skill_str = page.evaluate("getPlayerTotalStat('STR')")
        assert res_skill_str == 10, f"Expected base(5) + equip(2) + skill(3) = 10, got {res_skill_str}"

        # Test case 5: Skill bonus for END
        # "Reinforced Vitality" level 2 gives +5 END
        page.evaluate('''() => {
            player.stats.END = 4;
            player.skills["Reinforced Vitality"] = 2;
        }''')
        res_skill_end = page.evaluate("getPlayerTotalStat('END')")
        assert res_skill_end == 9, f"Expected base(4) + skill(5) = 9, got {res_skill_end}"

        # Test case 6: Skill bonus for AGI
        # "Fleet Footed" level 3 gives +7 AGI
        page.evaluate('''() => {
            player.stats.AGI = 3;
            player.skills["Fleet Footed"] = 3;
        }''')
        res_skill_agi = page.evaluate("getPlayerTotalStat('AGI')")
        assert res_skill_agi == 10, f"Expected base(3) + skill(7) = 10, got {res_skill_agi}"

        # Test case 7: Skill bonus for FOC
        # "Inner Sight" level 1 gives +3 FOC
        page.evaluate('''() => {
            player.stats.FOC = 2;
            player.skills["Inner Sight"] = 1;
        }''')
        res_skill_foc = page.evaluate("getPlayerTotalStat('FOC')")
        assert res_skill_foc == 5, f"Expected base(2) + skill(3) = 5, got {res_skill_foc}"

        print("All getPlayerTotalStat tests passed successfully!")

        browser.close()

if __name__ == "__main__":
    test_get_player_total_stat()
