import sys, os, datetime
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.getcwd())
from logistics_box import SessionManager, Database
try: name = input("Macro Name: ").strip()
except: name=""
if not name: name = f"Macro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
Database.init()
SessionManager.open_manual_session(record_mode=True, macro_name=name)