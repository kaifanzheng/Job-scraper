import pyautogui

print("🔍 Click anywhere on the screen. Press 'Esc' to exit.")

while True:

    if pyautogui.mouseDown():  # Detects left mouse click
        x, y = pyautogui.position()  # Get current mouse position
        print(f"🖱 Mouse clicked at: X={x}, Y={y}")
        pyautogui.sleep(0.5)  # Small delay to avoid duplicate prints
