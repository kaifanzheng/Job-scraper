import pyautogui
import random
# print("Move your mouse! Press 'Ctrl + C' to stop.")

# try:
#     while True:
#         x, y = pyautogui.position()
#         print(f"🖱 Current Mouse Position: X={x}, Y={y}", end="\r")
# except KeyboardInterrupt:
#     print("\n✅ Stopped tracking mouse position.")

pyautogui.moveTo(200, 500, duration=random.uniform(0.5, 1.5))