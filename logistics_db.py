import streamlit as st
import pandas as pd
import sqlite3
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# ==========================================
# PART 1: THE DATABASE ENGINE
# ==========================================
class Database:
    DB_FILE = "logistics.db"

    @staticmethod
    def init():
        conn = sqlite3.connect(Database.DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      customer TEXT,
                      raw_message TEXT UNIQUE,
                      date_found TEXT,
                      status TEXT,
                      product TEXT,
                      value REAL,
                      address TEXT,
                      city TEXT)''')
        conn.commit()
        conn.close()

    @staticmethod
    def save_order(customer, msg, date):
        conn = sqlite3.connect(Database.DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO orders (customer, raw_message, date_found, status) VALUES (?, ?, ?, ?)",
                      (customer, msg, date, "New"))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def fetch_all():
        conn = sqlite3.connect(Database.DB_FILE)
        df = pd.read_sql_query("SELECT * FROM orders", conn)
        conn.close()
        return df

    @staticmethod
    def update_analysis(order_id, product, value, address, city, status="Analyzed"):
        conn = sqlite3.connect(Database.DB_FILE)
        c = conn.cursor()
        c.execute('''UPDATE orders 
                     SET product=?, value=?, address=?, city=?, status=? 
                     WHERE id=?''', 
                  (product, value, address, city, status, order_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_order(order_id):
        conn = sqlite3.connect(Database.DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()
        conn.close()

# ==========================================
# PART 2: THE SCRAPER ENGINE
# ==========================================
class ScraperBot:
    @staticmethod
    def run(limit_count, limit_days):
        print(f"DEBUG: Indexing last {limit_days} days...")
        targets = InboxIndexer.build_target_list(limit_count, limit_days)
        if not targets: return []
        print(f"DEBUG: Found {len(targets)} targets. Fetching details...")
        return SafeWorker.fetch_details(targets)

class InboxIndexer:
    @staticmethod
    def parse_date(date_str):
        now = datetime.now()
        clean = date_str.strip().lower()
        try:
            if any(x in clean for x in ['min', 'hr', 'now', 'just']): return now
            if 'yesterday' in clean: return now - timedelta(days=1)
            if re.search(r'[a-z]{3}\s\d+', clean): return datetime.strptime(clean + f" {now.year}", "%b %d %Y")
        except: pass
        return now - timedelta(days=365)

    @staticmethod
    def build_target_list(limit_count, limit_days):
        targets = []
        cutoff = datetime.now() - timedelta(days=limit_days)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state="fb_auth.json")
            page = context.new_page()
            page.goto("https://mbasic.facebook.com/messages/")
            keep_scanning = True
            while keep_scanning and len(targets) < limit_count:
                threads = page.query_selector_all("table h3")
                if not threads: break
                for thread in threads:
                    if len(targets) >= limit_count: break
                    try:
                        name = thread.inner_text()
                        anchor = thread.query_selector("xpath=ancestor::a")
                        if not anchor: continue
                        full_link = "https://mbasic.facebook.com" + anchor.get_attribute("href")
                        row = thread.query_selector("xpath=ancestor::tr")
                        abbr = row.query_selector("abbr")
                        time_str = abbr.inner_text() if abbr else "Today"
                        if InboxIndexer.parse_date(time_str) >= cutoff:
                            targets.append({"name": name, "url": full_link, "date": time_str})
                        else:
                            keep_scanning = False; break
                    except: continue
                next_btn = page.query_selector("#see_older_threads a")
                if next_btn: next_btn.click()
                else: keep_scanning = False
            browser.close()
        return targets

class SafeWorker:
    @staticmethod
    def fetch_details(target_list):
        data = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state="fb_auth.json")
            page = context.new_page()
            for t in target_list:
                try:
                    page.goto(t['url'])
                    raw_text = page.inner_text("div#root")
                    lines = [l for l in raw_text.split('\n') if len(l) > 10]
                    clean_msg = " || ".join(lines[-10:])
                    data.append({"customer": t['name'], "raw_message": clean_msg, "date": t['date']})
                except: pass
            browser.close()
        return data

# ==========================================
# PART 3: BUSINESS LOGIC
# ==========================================
class Analyzer:
    @staticmethod
    def apply_pricing_logic(df, schema):
        for _, row in df.iterrows():
            text = row['raw_message']
            prod_name, val, city = "Unsure", 0, "Unknown"
            
            for item in schema:
                if any(k.strip().lower() in text.lower() for k in item['keywords'].split(',')):
                    prod_name = item['name']; val = item['price']; break
            
            towns = ["Longview", "Tyler", "Marshall", "Kilgore", "Gladewater"]
            for t in towns:
                if t.lower() in text.lower(): city = t; break
            
            addr = None
            match = re.search(r'\d{2,5}\s\w+\s?(?:St|Ave|Rd|Dr|Hwy|Ln|Blvd)\w*', text, re.IGNORECASE)
            if match: addr = match.group(0) + (f", {city}, TX" if city != "Unknown" else "")
            
            Database.update_analysis(row['id'], prod_name, val, addr, city)

# ==========================================
# PART 4: THE DASHBOARD UI
# ==========================================
def main():
    st.set_page_config(layout="wide", page_title="Logistics DB")
    Database.init()
    st.title("📦 Logistics Command Center")

    st.sidebar.header("Configuration")
    if 'schema' not in st.session_state:
        st.session_state.schema = [
            {"name": "Full Cord", "price": 300, "keywords": "full cord, 1 cord", "reply": "A Full Cord is $300..."},
            {"name": "Half Cord", "price": 175, "keywords": "half cord, 1/2", "reply": "Half Cord is $175..."}
        ]
    
    schema = st.session_state.schema
    for i, p in enumerate(schema):
        with st.sidebar.expander(f"{p['name']}"):
            p['price'] = st.number_input(f"Price", value=p['price'], key=f"p{i}")
            p['reply'] = st.text_area("Reply Template", value=p['reply'], key=f"r{i}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬇️ SCRAPE MESSAGES"):
            new_data = ScraperBot.run(15, 14)
            count = 0
            for item in new_data:
                if Database.save_order(item['customer'], item['raw_message'], item['date']): count += 1
            st.success(f"Imported {count} new orders!")

    with c2:
        if st.button("💲 RE-APPLY PRICING"):
            df = Database.fetch_all()
            Analyzer.apply_pricing_logic(df, schema)
            st.success("Prices updated!")

    df_db = Database.fetch_all()
    if not df_db.empty:
        st.metric("Total Revenue", f"${df_db['value'].sum()}")
        cities = df_db['city'].unique()
        tabs = st.tabs([c if c else "Unknown" for c in cities])
        
        for city, tab in zip(cities, tabs):
            with tab:
                subset = df_db[df_db['city'] == city]
                addrs = subset[subset['address'].notnull()]['address'].tolist()
                if addrs:
                    link = "https://www.google.com/maps/dir/" + "/".join([a.replace(" ", "+") for a in addrs])
                    st.markdown(f"**[🗺️ ROUTE FOR {city}]({link})**")
                
                for _, row in subset.iterrows():
                    with st.expander(f"{row['customer']} - {row['product']} (${row['value']})"):
                        st.write(row['raw_message'])
                        tpl = next((p['reply'] for p in schema if p['name'] == row['product']), "Hi!")
                        st.text_area("Draft Reply", tpl, key=f"rp_{row['id']}")
                        if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                            Database.delete_order(row['id']); st.rerun()

if __name__ == "__main__":
    main()
