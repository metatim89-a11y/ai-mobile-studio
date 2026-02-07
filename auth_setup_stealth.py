from playwright.sync_api import sync_playwright
import time
import random

def login_and_save_state():
    with sync_playwright() as p:
        # LAUNCH WITH STEALTH ARGUMENTS
        # These flags tell Chrome to hide the "Automation" banner that Facebook looks for.
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--no-sandbox", 
                "--disable-infobars"
            ]
        )
        
        # CREATE A CONTEXT WITH A REAL USER AGENT
        # This makes the bot look like a standard Windows Laptop to Facebook.
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()

        # REMOVE "webdriver" PROPERTY
        # This is a technical trick to hide the robot controls from Facebook's javascript.
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        print("--- STEALTH MODE ENGAGED ---")
        print("1. I am opening Facebook.")
        print("2. Please log in manually.")
        print("3. IF YOU SEE A BLOCK: Stop and wait 24 hours.")
        print("4. When you see your Feed/Messages, come back here and press ENTER.")
        
        page.goto("https://www.facebook.com/")
        
        # Wait for user input
        input("Press Enter here once you are fully logged in...")

        # Save the cookies to the file
        context.storage_state(path="fb_auth.json")
        print("✅ Session saved to 'fb_auth.json'.")
        
        browser.close()

if __name__ == "__main__":
    login_and_save_state()
