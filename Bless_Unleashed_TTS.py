import tkinter as tk
from tkinter.ttk import Scale
from pyttsx3 import init as tts_init
import pytesseract
from PIL.ImageGrab import grab
from PIL.ImageTk import PhotoImage
from PIL import Image
import threading
from re import search

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Ben\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def read_text_from_screen(screen_region=None):
    if screen_region is not None:
        screenshot = grab(bbox=screen_region)
    else:
        screenshot = grab()

    screenshot = screenshot.convert('L')
    text = pytesseract.image_to_string(screenshot)
    return text

def pyttsx3_text_to_speech(text, speed, after_speech):
    global stop_event
    tts = tts_init()
    voices = tts.getProperty("voices")
    tts.setProperty("voice", voices[1].id)
    tts.setProperty("rate", speed)

    for word in "".join(text.split("\n")).split("."):
        if stop_event and stop_event.is_set():
            return  # Check stop event before each chunk
        tts.say(word)
        tts.runAndWait()

    # Call the after_speech function when speech is finished
    after_speech()

def bless_unleashed_tts(text, text_widget, speed_slider, volume_button, stop_label, root, speed_label, speed_entry):
    text_widget.config(state=tk.NORMAL)  # Enable editing
    text_widget.delete(1.0, tk.END)  # Clear previous text
    text_widget.insert(tk.END, text, "center")  # Insert new text with the "center" tag
    text_widget.config(state=tk.DISABLED)  # Disable editing

    # Get the user input speed from the slider widget and round to 2 decimal places
    speed = round(speed_slider.get(), 2)
    speed_label.config(text=f"Speed: {speed} WPM")  # Update the speed label

    # Disable the volume button during speech
    volume_button.config(state=tk.DISABLED)

    # Change the volume button image to stop icon during speech
    volume_button.config(image=stop_icon)

    def after_speech():
        # Re-enable the volume button after speech is finished
        volume_button.config(state=tk.NORMAL)
        # Change the volume button image back to play icon after speech
        volume_button.config(image=play_icon)

    def speech_thread():
        global stop_event
        tts = tts_init()
        voices = tts.getProperty("voices")
        tts.setProperty("voice", voices[1].id)
        tts.setProperty("rate", speed)

        for word in "".join(text.split("\n")).split("."):
            if stop_event and stop_event.is_set():
                # Change the volume button image back to play icon if speech is stopped
                volume_button.config(image=play_icon)
                return  # Check stop event before each chunk
            tts.say(word)
            tts.runAndWait()

        # Call the after_speech function when speech is finished
        after_speech()

    # Run text-to-speech in a separate thread with the specified speed
    threading.Thread(target=speech_thread).start()

    # Update the text widget height based on the content
    update_text_widget_height(text_widget)

    # Update the positions of widgets to keep them centered
    update_positions(root, text_widget, volume_button, stop_label, speed_slider, speed_label, speed_entry)

    # Re-enable the volume button after speech is finished
    volume_button.config(state=tk.NORMAL)

def update_text_widget_height(text_widget):
    # Adjust the height of the text widget based on the content
    text_widget_height = int(text_widget.count("1.0", tk.END, "displaylines")[0])
    text_widget.config(height=text_widget_height)

def on_button_click(frame, text_widget, speed_slider, volume_button, root, stop_label, speed_label, speed_entry, min_thread_count):
    global stop_event
    text = read_text_from_screen((450, 880, 1450, 1000))
    if stop_event and stop_event.is_set():
        # Create a new stop event to signal when to stop the speech
        stop_event = threading.Event()
    if threading.active_count() == min_thread_count:
        bless_unleashed_tts(text, text_widget, speed_slider, volume_button, stop_label, root, speed_label, speed_entry)
    else:
        on_stop_button_click(volume_button)

def on_stop_button_click(volume_button):
    global stop_event
    stop_event.set()

    # Change the volume button image back to play icon
    volume_button.config(image=play_icon)

def on_enter(event):
    volume_button.config(bg="lightblue")

def on_leave(event):
    volume_button.config(bg="SystemButtonFace")

def on_slider_move(event, speed_slider, speed_label):
    speed = round(speed_slider.get(), 2)
    speed_label.config(text=f"Speed: {speed} WPM")

def on_speed_label_click(event, speed_label, speed_entry):
    # Calculate speed_label_height after the GUI components are set up
    speed_label_height = root.winfo_height() // 1.15

    # Clear the current text in the entry
    speed_entry.delete(0, tk.END)

    # Create a speed entry and place it between the normal speed text and the stop button
    speed_entry.place(x=root.winfo_width() // 2, y=(speed_label_height + root.winfo_height() // 1.5) / 2, anchor="center")
    speed_entry.focus_set()
    speed_entry.bind("<Return>", lambda e: update_speed_from_entry(speed_entry, speed_label, speed_slider))
    #speed_entry.bind("<FocusOut>", lambda e: update_speed_from_entry(speed_entry, speed_label, speed_slider))

def update_speed_from_entry(speed_entry, speed_label, speed_slider):
    current_text = speed_label.cget("text")

    try:
        new_speed = float(speed_entry.get())
        if 0 <= new_speed <= 500:
            speed_slider.set(new_speed)
            speed_label.config(text=f"Speed: {new_speed} WPM")
        else:
            # Reset the label to the current speed if the entry is out of bounds
            current_speed = float(search(r"\d+\.\d+", current_text).group()) if search(r"\d+\.\d+", current_text) else 0.0
            speed_entry.delete(0, tk.END)
            speed_entry.insert(0, current_speed)
    except ValueError:
        # Reset the label to the current speed if the entry is not a valid number
        current_speed = float(search(r"\d+\.\d+", current_text).group()) if search(r"\d+\.\d+", current_text) else 0.0
        speed_entry.delete(0, tk.END)
        speed_entry.insert(0, current_speed)
    finally:
        # Withdraw the entry after updating the speed
        speed_entry.place_forget()


# Update the positions of widgets to keep them centered
def update_positions(root, text_widget, volume_button, stop_label, speed_slider, speed_label, speed_entry):
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    # List of widgets to get dimensions
    widgets = [text_widget, volume_button, stop_label, speed_slider, speed_label]

    if speed_entry.winfo_ismapped():
        widgets.append(speed_entry)

    dimensions = [(i.winfo_reqwidth(), i.winfo_reqheight()) for i in widgets]

    # Update the positions of widgets to keep them centered
    text_widget.place(x=window_width // 2, y=window_height // 2 - dimensions[1][1]-25, anchor="center")
    volume_button.place(x=window_width // 2, y=window_height // 2, anchor="center")
    stop_label.place(x=window_width // 2, y=(stop_label_height := (window_height + dimensions[1][1] + dimensions[2][1]) // 2), anchor="center")
    speed_label.place(x=window_width // 2, y=(speed_label_height := stop_label_height + dimensions[4][1] + 30), anchor="center")
    if speed_entry.winfo_ismapped():
        speed_entry.place(x=window_width // 2, y=(speed_label_height + root.winfo_height() // 1.5) / 2, anchor="center")
    speed_slider.place(x=window_width // 2, y=speed_label_height + 25, anchor="center")

    # Adjust the minimum size based on the dimensions of the text, button, stop button, slider, and speed label with an extra 10-pixel gap
    text_width = text_widget.winfo_reqwidth()
    text_height = text_widget.winfo_reqheight()
    volume_button_width = volume_button.winfo_reqwidth()
    volume_button_height = volume_button.winfo_reqheight()
    stop_label_width = stop_label.winfo_reqwidth()
    stop_label_height = stop_label.winfo_reqheight()
    speed_slider_width = speed_slider.winfo_reqwidth()
    speed_slider_height = speed_slider.winfo_reqheight()

    # Set the minimum size for the root window
    root.minsize(text_width + 20, text_height + volume_button_height + speed_slider_height + stop_label_height + 125)

# Create the main window
root = tk.Tk()
root.iconphoto(False, PhotoImage(file = "title_icon.png"))
root.title("Bless Unleashed Text To Speech")
min_thread_count = threading.active_count()
# Adjust the minimum size based on the dimensions of the text, button, stop button, slider, and speed label with an extra 10-pixel gap
text_width = 40
text_height = 5
volume_button_width = 100
volume_button_height = 100
stop_label_width = 10  # guessed
stop_label_height = 5  # guessed
speed_slider_width = 200
speed_slider_height = 10  # guessed
# Set the minimum size for the root window with a 10-pixel gap
window_width = 384
window_height = text_height + volume_button_height + speed_slider_height + stop_label_height + 10

# Create a Text widget to display the text with a minimum height and width
text_widget = tk.Text(root, wrap=tk.WORD, font=("Helvetica", 12), state=tk.DISABLED, width=text_width, height=text_height)
text_widget.place(x=window_width // 2, y=window_height // 3, anchor="center")
# Configure a tag for center alignment
text_widget.tag_configure("center", justify="center")

# Load play and stop icons
play_icon_path = "play_icon.png"  # Replace with the actual path to your play icon image
stop_icon_path = "stop_icon.png"  # Replace with the actual path to your stop icon image
original_play_icon = Image.open(play_icon_path)
resized_play_icon = original_play_icon.resize((volume_button_width, volume_button_height), Image.Resampling.LANCZOS)
play_icon = PhotoImage(resized_play_icon)
original_stop_icon = Image.open(stop_icon_path)
resized_stop_icon = original_stop_icon.resize((volume_button_width, volume_button_height), Image.Resampling.LANCZOS)
stop_icon = PhotoImage(resized_stop_icon)
# Create a button with the resized play icon and fixed size, associate on_button_click with its click event
volume_button = tk.Button(root, image=play_icon, width=volume_button_width, height=volume_button_height, state=tk.NORMAL)
volume_button.place(x=window_width // 2, y=window_height // 2, anchor="center")

# Create a stop button with a fixed size, associate on_stop_button_click with its click event
#stop_button = tk.Button(root, text="Stop After This Sentence", command=lambda: on_stop_button_click(volume_button))
stop_label = tk.Label(root, text="(Only Stops After The Current Sentence)")
stop_label.place(x=window_width // 2, y=window_height // 1.5, anchor="center")

# Create a slider for speech speed
speed_slider = Scale(root, from_=0, to=500, orient="horizontal", length=speed_slider_width)
speed_slider.place(x=window_width // 2, y=window_height // 1.2, anchor="center")
default_speed = 225
speed_slider.set(default_speed)  # Default speed

# Create a label to display the current speed
speed_label = tk.Label(root, text=f"Speed: {default_speed} WPM")
speed_label.place(x=window_width // 2, y=window_height // 1.15, anchor="center")

# Create a stop event to signal when to stop the speech
global stop_event
stop_event = threading.Event()

# Create a speed entry widget
speed_entry = tk.Entry(root)
speed_entry.place_forget()  # Initially hide the entry

# Associate on_button_click with the button click event
volume_button.config(
    command=lambda: on_button_click(root, text_widget, speed_slider, volume_button, root, stop_label, speed_label, speed_entry, min_thread_count))

# Bind events for when the cursor enters or leaves the button
volume_button.bind("<Enter>", on_enter)
volume_button.bind("<Leave>", on_leave)

# Bind the slider movement to the update of the speed label
speed_slider.bind("<B1-Motion>", lambda event: on_slider_move(event, speed_slider, speed_label))
speed_slider.bind("<ButtonRelease-1>", lambda event: on_slider_move(event, speed_slider, speed_label))

# Bind the speed label click event to the function
speed_label.bind("<Button-1>", lambda event: on_speed_label_click(event, speed_label, speed_entry))

# Bind the window resize event to update the widget positions
root.bind("<Configure>", lambda event: update_positions(root, text_widget, volume_button, stop_label, speed_slider, speed_label, speed_entry))
root.protocol("WM_DELETE_WINDOW", root.quit()) 
# Start the main loop to run the application
root.mainloop()
