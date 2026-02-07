import json

# This is the exact data you provided
cookie_string = "datr=dS93aSvTE4Rc1jS07ViTaHOG; sb=dS93aYaYD2mxtVq7MVWBGodU; ps_l=1; ps_n=1; c_user=100055913533580; dpr=1.125; fr=1Ed5GHGeF9ohvnlzd.AWe9bpItcHToBSGY_QXXxNttQ_joUj5ryq3gu7Wgx3fW4kVgGio.BphUSh..AAA.0.0.BphUSh.AWca8AsK_1eDkETvfjHDkwg9rM0; xs=16%3AXfZfwIRhOzfeHQ%3A2%3A1769442735%3A-1%3A-1%3A%3AAcySByddebw_m_C2D_Vkls6QIAAnqena5Izfe_0hB9Q; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1770342226659%2C%22v%22%3A1%7D; wd=204x873"

cookies = []
for item in cookie_string.split(';'):
    if '=' in item:
        name, value = item.split('=', 1)
        cookies.append({
            "name": name.strip(),
            "value": value.strip(),
            "domain": ".facebook.com",
            "path": "/",
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax"
        })

storage_state = {
    "cookies": cookies,
    "origins": [
        {
            "origin": "https://www.facebook.com",
            "localStorage": []
        }
    ]
}

with open("fb_auth.json", "w") as f:
    json.dump(storage_state, f, indent=2)

print("✅ SUCCESS: Your cookie has been implanted into 'fb_auth.json'.")
