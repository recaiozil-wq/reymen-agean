import os
import sys
from playwright.sync_api import sync_playwright
import logging
logger = logging.getLogger(__name__)


def main():
    print(f"Python: {sys.executable}")

    user_data_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
    cookies_path = os.path.join(os.path.dirname(__file__), "cookies.json")

    if not os.path.exists(user_data_dir):
        print(f"[WARN] Chrome User Data not found: {user_data_dir}")
        print("[ACTION] Use cookies.json injection with Playwright Chromium instead.")
        use_chrome_profile = False
    else:
        use_chrome_profile = True

    if use_chrome_profile and not input("[OK] Normal Chrome is closed; continue with Chrome profile? [y/N] ").strip().lower().startswith("y"):
        print("Aborted by user.")
        return

    with sync_playwright() as p:
        if use_chrome_profile:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                channel="chrome",
                viewport={"width": 1280, "height": 720},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
            )
        else:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
            )
            context = browser.new_context(viewport={"width": 1280, "height": 720})

            if cookies_path and os.path.exists(cookies_path):
                import json

                with open(cookies_path, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                context.add_cookies(cookies)
                print(f"[OK] Loaded cookies from: {cookies_path}")
            else:
                print(f"[WARN] Missing cookies.json at: {cookies_path}")

        page = context.new_page()
        try:
            target_url = "https://www.sahibinden.com/kentsel-donusum-istanbul"
            print(f"-> Navigating: {target_url}")
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            print(f"Page title: {page.title()}")
        except Exception as e:
            print(f"[ERROR] {e}")

        print("Press ENTER to close...")
        try:
            input()
        except EOFError:
            logger.warning("[fix_01_sessiz_except] EOFError")

        context.close()
        if not use_chrome_profile:
            browser.close()


if __name__ == "__main__":
    main()
