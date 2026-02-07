import streamlit as st
import pandas as pd
import sqlite3
import time
import json
import re
import logging
import threading
import sys
import os
import datetime
import subprocess
from playwright.sync_api import sync_playwright

# ==========================================
# PART 0: SYSTEM LOGGING & STYLING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("LogisticsBox")

def setup_style():
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: white; }
        .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
        .st-card { 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #41444e; 
            background: #161b22; 
            margin-bottom: 20px; 
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# PART 1: PERSISTENT DATABASE ENGINE
# ==========================================
class Database:
    DB_FILE = "logistics_deep.db"

    @staticmethod
    def init():
        conn = sqlite3.connect(Database.DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS deep_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_profile TEXT, raw_message TEXT, 
                      keyword_found TEXT, scanned_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS watchlist
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS macros
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, steps JSON)''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_state 
                     (id INTEGER PRIMARY KEY, autopilot_active INTEGER, interval TEXT)''')
        c.execute("INSERT OR IGNORE INTO system_state (id, autopilot_active, interval) VALUES (1, 0, '1 hour')")
        conn.commit()
        conn.close()

# ==========================================
# PART 2: AUTOMATED LOGIN & MACRO TOOLS
# ==========================================
class AutomationTools:
    @staticmethod
    def run_auto_login():
        """Opens a browser for the user to log in and saves the state automatically."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False) 
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.facebook.com")
            
            while True:
                try:
                    if page.is_closed(): break
                    if "messages" in page.url:
                        context.storage_state(path="fb_auth.json")
                        logger.info("Session captured and saved to fb_auth.json")
                        break
                    time.sleep(1)
                except: break
            browser.close()

    @staticmethod
    def record_macro(name):
        """Records clicks and keys to create a reusable automation script."""
        steps = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state="fb_auth.json" if os.path.exists("fb_auth.json") else None)
            page = context.new_page()
            
            page.expose_function("log_step", lambda data: steps.append(data))
            page.add_init_script("""
                document.addEventListener('mousedown', e => {
                    window.log_step({type: 'click', x: e.clientX, y: e.clientY, ts: Date.now()});
                });
                document.addEventListener('keydown', e => {
                    window.log_step({type: 'keypress', key: e.key, ts: Date.now()});
                });
            """)
            
            page.goto("https://www.facebook.com/messages/t/")
            while True:
                try:
                    if page.is_closed(): break
                    time.sleep(1)
                except: break
            
            if steps:
                conn = sqlite3.connect(Database.DB_FILE)
                conn.execute("INSERT INTO macros (name, steps) VALUES (?, ?)", (name, json.dumps(steps)))
                conn.commit()
                conn.close()
                return True
            return False

# ==========================================
# PART 3: THE PASSIVE SCRAPER
# ==========================================
class PassiveScanner:
    @staticmethod
    def run_scan():
        Database.init()
        conn = sqlite3.connect(Database.DB_FILE)
        watch_words = pd.read_sql("SELECT word FROM watchlist", conn)['word'].tolist()
        conn.close()

        if not watch_words: return

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True) 
                if not os.path.exists("fb_auth.json"): return
                
                context = browser.new_context(storage_state="fb_auth.json")
                page = context.new_page()
                page.goto("https://www.facebook.com/messages/t/", timeout=60000)
                page.wait_for_selector("div[role='grid']", timeout=30000)
                chats = page.locator("div[role='row']").all()
                
                for chat in chats:
                    raw_text = chat.inner_text()
                    for word in watch_words:
                        if re.search(re.escape(word), raw_text, re.IGNORECASE):
                            lines = raw_text.split('\n')
                            user_name = lines[0] if lines else "Unknown"
                            conn = sqlite3.connect(Database.DB_FILE)
                            exists = conn.execute("SELECT 1 FROM deep_logs WHERE user_profile=? AND raw_message=?", (user_name, raw_text)).fetchone()
                            if not exists:
                                conn.execute("INSERT INTO deep_logs (user_profile, raw_message, keyword_found, scanned_at) VALUES (?, ?, ?, ?)",
                                             (user_name, raw_text.replace('\n', ' '), word, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
                                conn.commit()
                            conn.close()
                            break 
                browser.close()
        except Exception as e: logger.error(f"Scraper Error: {e}")

# ==========================================
# PART 4: SCHEDULER & UI
# ==========================================
class Scheduler:
    INTERVAL_MAP = {"2 min": 120, "5 min": 300, "10 min": 600, "30 min": 1800, "1 hour": 3600, "2 hours": 7200, "28 hours": 100800}

    @staticmethod
    def background_loop():
        while True:
            conn = sqlite3.connect(Database.DB_FILE)
            state = conn.execute("SELECT autopilot_active, interval FROM system_state WHERE id=1").fetchone()
            conn.close()
            if state and state[0]:
                PassiveScanner.run_scan()
                time.sleep(Scheduler.INTERVAL_MAP.get(state[1], 3600))
            else: time.sleep(5)

def main():
    st.set_page_config(layout="wide", page_title="Logistics Box")
    setup_style()
    Database.init()

    if not any(t.name == "HunterLoop" for t in threading.enumerate()):
        threading.Thread(target=Scheduler.background_loop, name="HunterLoop", daemon=True).start()

    st.title("📦 Logistics Intelligence Box")
    
    # SYSTEM CONTROLS
    with st.sidebar:
        st.header("🛠️ Toolbelt")
        if st.button("🔑 Start Auto-Login Bot"):
            with st.spinner("Opening browser... Log in and go to Messages to save session."):
                AutomationTools.run_auto_login()
                st.success("Session updated!")
                st.rerun()

        st.divider()
        m_name = st.text_input("New Macro Name", "Reply_Firewood")
        if st.button("🔴 Record New Macro"):
            with st.spinner("Recording... Close browser when done."):
                if AutomationTools.record_macro(m_name):
                    st.success(f"Macro '{m_name}' saved!")
                    time.sleep(1)
                    st.rerun()

    # MAIN TABS
    tab_dash, tab_logs, tab_watch, tab_macros = st.tabs(["🎮 Control", "📚 Database", "🎯 Watchlist", "🔴 Macros"])

    with tab_dash:
        conn = sqlite3.connect(Database.DB_FILE)
        active, current_interval = conn.execute("SELECT autopilot_active, interval FROM system_state WHERE id=1").fetchone()
        conn.close()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("System Status", "RUNNING" if active else "IDLE")
            if st.button("🚀 ENGAGE" if not active else "🛑 STOP"):
                conn = sqlite3.connect(Database.DB_FILE)
                conn.execute("UPDATE system_state SET autopilot_active=? WHERE id=1", (0 if active else 1,))
                conn.commit(); conn.close()
                st.rerun()
        with col2:
            freq = st.selectbox("Interval", list(Scheduler.INTERVAL_MAP.keys()), index=list(Scheduler.INTERVAL_MAP.keys()).index(current_interval))
            if st.button("Update Frequency"):
                conn = sqlite3.connect(Database.DB_FILE)
                conn.execute("UPDATE system_state SET interval=? WHERE id=1", (freq,))
                conn.commit(); conn.close()
                st.rerun()

    with tab_logs:
        st.subheader("Deep Logs (Keyword Matches)")
        df = pd.read_sql("SELECT * FROM deep_logs ORDER BY id DESC", sqlite3.connect(Database.DB_FILE))
        st.dataframe(df, use_container_width=True)

    with tab_watch:
        st.subheader("Manage Tracking Phrases")
        new_w = st.text_input("Add Tracking Phrase")
        if st.button("Add"):
            conn = sqlite3.connect(Database.DB_FILE)
            conn.execute("INSERT OR IGNORE INTO watchlist (word) VALUES (?)", (new_w,))
            conn.commit(); conn.close()
            st.rerun()
        
        words = pd.read_sql("SELECT * FROM watchlist", sqlite3.connect(Database.DB_FILE))
        for _, row in words.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(f"🔍 {row['word']}")
            if c2.button("🗑️", key=f"word_{row['id']}"):
                conn = sqlite3.connect(Database.DB_FILE)
                conn.execute("DELETE FROM watchlist WHERE id=?", (row['id'],))
                conn.commit(); conn.close(); st.rerun()

    with tab_macros:
        st.subheader("Saved Macros")
        macros_df = pd.read_sql("SELECT * FROM macros ORDER BY id DESC", sqlite3.connect(Database.DB_FILE))
        if not macros_df.empty:
            for _, row in macros_df.iterrows():
                steps = json.loads(row['steps'])
                with st.expander(f"🎬 {row['name']} ({len(steps)} steps)"):
                    st.json(steps)
                    if st.button("🗑️ Delete Macro", key=f"macro_{row['id']}"):
                        conn = sqlite3.connect(Database.DB_FILE)
                        conn.execute("DELETE FROM macros WHERE id=?", (row['id'],))
                        conn.commit(); conn.close(); st.rerun()
        else:
            st.info("No macros recorded yet. Use the sidebar to record your first action.")

if __name__ == "__main__":
    main()