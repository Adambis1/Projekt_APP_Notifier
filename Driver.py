import subprocess
import threading

threading.Thread(target=subprocess.run, args=['py Facebook.py']).start()
threading.Thread(target=subprocess.run, args=['py Telegram.py']).start()