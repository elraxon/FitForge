const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('FitForge Game Logic Tests', () => {
    test.beforeEach(async ({ page }) => {
        // Load the HTML content directly
        const htmlPath = path.resolve(__dirname, '..', 'FitForgeV1.html');
        const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
        await page.setContent(htmlContent);
    });

    test('d10() should return random integers between 1 and 10', async ({ page }) => {
        const results = await page.evaluate(() => {
            const vals = new Set();
            for (let i = 0; i < 50; i++) {
                vals.add(d10());
            }
            return Array.from(vals);
        });

        expect(results.length).toBeGreaterThan(1);
        for (const val of results) {
            expect(Number.isInteger(val)).toBeTruthy();
            expect(val).toBeGreaterThanOrEqual(1);
            expect(val).toBeLessThanOrEqual(10);
        }
    });

    test('calculateDerivedStats() should compute stats correctly', async ({ page }) => {
        // Unlock stats and bypass tutorial
        await page.evaluate(() => {
            unlockAllCoreStatsAndGrantGear();

            player.stats.STR = 5;
            player.stats.END = 4;
            player.stats.AGI = 6;
            player.stats.FOC = 3;
            player.skills = {};
            player.equipment = {
                weapon: null, chest: null, shield: null, helmet: null,
                gloves: null, boots: null, amulet: null
            };

            calculateDerivedStats();
        });

        // Get the derived stats from the game logic
        const derivedStats = await page.evaluate(() => player.derivedStats);

        // Also get the base constants to compute the expected results
        const constants = await page.evaluate(() => {
            return {
                baseHp: BASE_HP,
                hpFromEnd: HP_FROM_END,
                hpFromStr: HP_FROM_STR,
                baseStamina: BASE_STAMINA,
                baseMana: BASE_MANA
            };
        });

        const expectedHp = constants.baseHp + (4 * constants.hpFromEnd) + (5 * constants.hpFromStr);
        const expectedStamina = constants.baseStamina + (4 * 5) + (6 * 7);
        const expectedMana = constants.baseMana + (3 * 8) + (4 * 3);

        expect(derivedStats.maxHp).toBe(expectedHp);
        expect(derivedStats.maxStamina).toBe(expectedStamina);
        expect(derivedStats.maxMana).toBe(expectedMana);
    });
});