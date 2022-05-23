import subprocess
import threading

threading.Thread(target=subprocess.run, args=['py Facebook.py']).start()
threading.Thread(target=subprocess.run, args=['py Telegram.py']).start()
threading.Thread(target=subprocess.run, args=['py Notifications_fb.py']).start()
threading.Thread(target=subprocess.run, args=['py Notifications_tg.py']).start()
