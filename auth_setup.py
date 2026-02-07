from playwright.sync_api import sync_playwright

def login_and_save_state():
    with sync_playwright() as p:
        # 1. Launch browser (Headless=False means you can SEE it)
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context()
        page = context.new_page()

        print("--- ACTION REQUIRED ---")
        print("1. I am opening Facebook.")
        print("2. Please log in manually in the browser window.")
        print("3. Handle any 2FA or codes.")
        print("4. When you see your Feed/Messages, come back here and press ENTER.")
        
        page.goto("https://www.facebook.com/messages/t/")
        
        # Wait for you to finish logging in
        input("Press Enter here once you are fully logged in...")

        # Save the cookies to a file
        context.storage_state(path="fb_auth.json")
        print(" Session saved to 'fb_auth.json'. The bot can now run automatically.")
        
        browser.close()

if __name__ == "__main__":
    login_and_save_state()
