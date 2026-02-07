import json
import os

def inject_cookies():
    print("\n🍪 --- FACEBOOK COOKIE INJECTOR --- 🍪")
    print("1. Open Chrome > F12 > Network Tab.")
    print("2. Refresh Facebook. Click the top request (www.facebook.com).")
    print("3. Scroll down to 'Request Headers' and copy the entire text next to 'Cookie:'.")
    print("------------------------------------------------------------------")
    
    # Get input safely (handles massive strings)
    print("\n👇 PASTE THE RAW COOKIE STRING BELOW AND PRESS ENTER:\n")
    try:
        raw_cookie_string = input().strip()
    except EOFError:
        print("\n❌ Error: Input stream closed unexpectedly.")
        return

    if not raw_cookie_string:
        print("\n❌ Error: No text pasted.")
        return

    # Clean up if they accidentally pasted "Cookie: " prefix
    if raw_cookie_string.lower().startswith("cookie:"):
        raw_cookie_string = raw_cookie_string.split(":", 1)[1].strip()

    # Parse the string 'key=value; key=value'
    cookies = []
    try:
        # Split by semicolon
        pairs = raw_cookie_string.split(';')
        
        for pair in pairs:
            if '=' in pair:
                # Split only on the first '=' to handle values containing '='
                name, value = pair.split('=', 1)
                
                cookie_obj = {
                    "name": name.strip(),
                    "value": value.strip(),
                    "domain": ".facebook.com",
                    "path": "/",
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax"
                }
                cookies.append(cookie_obj)
        
        if not cookies:
            print("\n❌ Error: Could not find any valid cookies in that string.")
            return

        # Create the Playwright auth structure
        storage_state = {
            "cookies": cookies,
            "origins": [
                {
                    "origin": "https://www.facebook.com",
                    "localStorage": []
                }
            ]
        }
        
        # Save to file
        filename = "fb_auth.json"
        with open(filename, "w") as f:
            json.dump(storage_state, f, indent=2)
            
        print(f"\n✅ SUCCESS! Parsed {len(cookies)} cookies.")
        print(f"📁 Saved to '{filename}'.")
        print("🚀 You can now run your bot.")

    except Exception as e:
        print(f"\n❌ parsing error: {e}")

if __name__ == "__main__":
    inject_cookies()