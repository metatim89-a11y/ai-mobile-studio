import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
with open("stop.signal", "w") as f: f.write("STOP")
print("Signal Sent to Parent Process.")