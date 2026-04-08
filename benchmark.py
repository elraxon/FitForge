from playwright.sync_api import sync_playwright
import time
import os

def test_performance():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        with open("FitForgeV1.html", "r") as f:
            html_content = f.read()

        page.set_content(html_content, timeout=0)

        # Setup state
        page.evaluate("""
            player.onboarding.nameSet = true;
            changeState('loggingExercise');
        """)

        # Run benchmark
        page.evaluate("""
            document.getElementById('lightMinutes').value = 10;
            document.getElementById('moderateMinutes').value = 20;
            document.getElementById('vigorousMinutes').value = 30;

            // Patch to avoid side effects that change the screen
            const originalChangeState = changeState;
            changeState = () => {};
            const originalAddLog = addLog;
            addLog = () => {};
            const originalUnlockAllCoreStatsAndGrantGear = unlockAllCoreStatsAndGrantGear;
            unlockAllCoreStatsAndGrantGear = () => {};
            const originalUpdateDisplay = updateDisplay;
            updateDisplay = () => {};
            const originalSaveGame = saveGame;
            saveGame = () => {};

            // Reset daily limits
            dailyGpEarnedFromExercise = 0;
            player.onboarding.lastExerciseDate = new Date().toDateString();

            let start = performance.now();
            for (let i = 0; i < 100000; i++) {
                // reset to avoid cap
                dailyGpEarnedFromExercise = 0;
                submitExercise();
            }
            let end = performance.now();
            window.benchmarkTime = end - start;

            changeState = originalChangeState;
            addLog = originalAddLog;
            unlockAllCoreStatsAndGrantGear = originalUnlockAllCoreStatsAndGrantGear;
            updateDisplay = originalUpdateDisplay;
            saveGame = originalSaveGame;
        """)

        time_taken = page.evaluate("window.benchmarkTime")
        print(f"Baseline Time for 100000 submitExercise calls: {time_taken:.2f} ms")

        browser.close()

if __name__ == "__main__":
    test_performance()