#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import re
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
from tkinter import Tk, Button, Label, Entry, StringVar, OptionMenu, Frame, DoubleVar
import time
import tkinter as tk

# Retry attempts and failed files list
MAX_RETRY_ATTEMPTS = 3
failed_files = {}

# Utility functions
def strip_quotes(path):
    return path.strip('\'"')

def sanitize_filename(filename):
    return re.sub(r'[\\/:\*\?"<>\|]', '', filename)

def show_warning_box(message):
    messagebox.showwarning("Warning", message)

def show_error_message(error_files):
    if error_files:
        error_message = "\n".join(f"{file}: {error}" for file, error in error_files.items())
        messagebox.showerror("Conversion Errors", f"The following files encountered errors:\n{error_message}")

# Browse functions
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

def browse_source_folder():
    folder_path = filedialog.askdirectory()
    entry_source_folder.delete(0, tk.END)
    entry_source_folder.insert(0, folder_path)

def browse_destination_folder():
    folder_path = filedialog.askdirectory()
    entry_destination_folder.delete(0, tk.END)
    entry_destination_folder.insert(0, folder_path)

# Conversion functions
def convert_audio(source_path, destination_path, output_format):
    try:
        # Try using MoviePy
        audio_clip = AudioFileClip(source_path)
        audio_clip.write_audiofile(destination_path, codec="libvorbis" if output_format == "ogg" else None)
        audio_clip.close()
    except Exception as e:
        print(f"MoviePy failed for {source_path}, trying pydub. Error: {e}")
        try:
            # Fallback to pydub if MoviePy fails
            audio = AudioSegment.from_file(source_path)
            audio.export(destination_path, format=output_format)
        except Exception as e:
            raise Exception(f"Audio conversion error: {e}")

def convert_image(source_path, destination_path, output_format):
    try:
        image = Image.open(source_path)
        image.save(destination_path, format=output_format)
    except Exception as e:
        raise Exception(f"Image conversion error: {e}")

# Retry logic
def process_file_with_retry(source_file_path, destination_file_path, destination_format, file_type, attempts=1):
    try:
        if file_type == 'audio':
            convert_audio(source_file_path, destination_file_path, destination_format)
        elif file_type == 'image':
            convert_image(source_file_path, destination_file_path, destination_format)
        return True  # Success
    except Exception as e:
        if attempts < MAX_RETRY_ATTEMPTS:
            print(f"Retry {attempts}/{MAX_RETRY_ATTEMPTS} for {source_file_path}")
            time.sleep(1)  # Add a small delay between retries
            return process_file_with_retry(source_file_path, destination_file_path, destination_format, file_type, attempts + 1)
        else:
            failed_files[source_file_path] = str(e)
            return False

# File processing
def copy_and_convert_files():
    excel_file_path = strip_quotes(entry_file.get())
    source_folder_path = strip_quotes(entry_source_folder.get())
    destination_folder_path = strip_quotes(entry_destination_folder.get())
    source_format = format_dropdown_source.get()
    destination_format = format_dropdown_destination.get()

    try:
        df = pd.read_excel(excel_file_path)
        total_files = len(df)
        progress_step = 100 / total_files if total_files > 0 else 1

        for index, row in df.iterrows():
            old_id = str(row['Source'])
            new_name = sanitize_filename(row['Destination'])

            # Handle "All" option for source format
            if source_format == "All":
                regex_pattern = re.compile(f"{re.escape(old_id)}.*")
            else:
                regex_pattern = re.compile(f"{re.escape(old_id)}\.{source_format}")

            matching_files = [filename for filename in os.listdir(source_folder_path) if regex_pattern.match(filename)]

            if matching_files:
                for matching_file in matching_files:
                    source_file_path = os.path.join(source_folder_path, matching_file)
                    file_extension = os.path.splitext(matching_file)[1].lstrip('.')
                    destination_file_name = f"{new_name}.{destination_format if destination_format != '-No conversion needed-' else file_extension}"
                    destination_file_path = os.path.join(destination_folder_path, destination_file_name)

                    # Determine file type (audio or image)
                    if file_extension in ['mp3', 'wav', 'flac', 'wma', 'amr', 'mmf', '3gp']:
                        file_type = 'audio'
                    elif file_extension in ['jpg', 'png', 'gif']:
                        file_type = 'image'
                    else:
                        file_type = None

                    try:
                        if destination_format == '-No conversion needed-':
                            shutil.copy(source_file_path, destination_file_path)
                        elif file_type:
                            process_file_with_retry(source_file_path, destination_file_path, destination_format, file_type)
                        else:
                            shutil.copy(source_file_path, destination_file_path)

                    except Exception as e:
                        print(f"An error occurred while processing {matching_file}: {e}")

            progress_var.set(progress_var.get() + progress_step)
            root.update_idletasks()

        show_error_message(failed_files)  # Show error messages after processing
        messagebox.showinfo("Success", "File copying and conversion process completed.")

    except Exception as e:
        show_warning_box(f"Error: {e}")

# Cancel operation function
def cancel_copy():
    root.destroy()

# Start the copy process in a separate thread
def start_copy_process():
    button_copy_files.config(state=tk.DISABLED)  # Disable button while processing
    threading.Thread(target=copy_and_convert_files).start()
    button_copy_files.config(state=tk.NORMAL)  # Re-enable button after processing

# Tkinter GUI setup
root = Tk()
root.title("File Copying and Conversion App")
root.geometry('600x500')

frame = Frame(root)
frame.pack(pady=20)

# Labels and Input Fields
label_file = Label(frame, text="Master Excel File:", font=("Arial", 12))
label_source_folder = Label(frame, text="Source Folder:", font=("Arial", 12))
label_destination_folder = Label(frame, text="Destination Folder:", font=("Arial", 12))
label_format_source = Label(frame, text="Source Format:", font=("Arial", 12))
label_format_destination = Label(frame, text="Convert to Format:", font=("Arial", 12))

label_file.grid(row=0, column=0, padx=10, pady=5)
label_source_folder.grid(row=1, column=0, padx=10, pady=5)
label_destination_folder.grid(row=2, column=0, padx=10, pady=5)
label_format_source.grid(row=3, column=0, padx=10, pady=5)
label_format_destination.grid(row=4, column=0, padx=10, pady=5)

entry_file = Entry(frame, font=("Arial", 12))
entry_source_folder = Entry(frame, font=("Arial", 12))
entry_destination_folder = Entry(frame, font=("Arial", 12))

entry_file.grid(row=0, column=1, padx=10, pady=5)
entry_source_folder.grid(row=1, column=1, padx=10, pady=5)
entry_destination_folder.grid(row=2, column=1, padx=10, pady=5)

button_browse_file = Button(frame, text="Browse", font=("Arial", 12), command=browse_file)
button_browse_source_folder = Button(frame, text="Browse", font=("Arial", 12), command=browse_source_folder)
button_browse_destination_folder = Button(frame, text="Browse", font=("Arial", 12), command= browse_destination_folder)

button_browse_file.grid(row=0, column=2, padx=10, pady=5)
button_browse_source_folder.grid(row=1, column=2, padx=10, pady=5)
button_browse_destination_folder.grid(row=2, column=2, padx=10, pady=5)

# Dropdowns for file format options
format_options = ["All", "mp3", "wav", "gif", "amr", "mmf", "3gp", "mp4", "jpg", "png", "flac", "wma"]
format_dropdown_source = StringVar(root)
format_dropdown_source.set(format_options[0])
format_menu_source = OptionMenu(frame, format_dropdown_source, *format_options)
format_menu_source.grid(row=3, column=1, padx=10, pady=5)

convert_options = ["-No conversion needed-"] + format_options[1:]
format_dropdown_destination = StringVar(root)
format_dropdown_destination.set(convert_options[0])
format_menu_destination = OptionMenu(frame, format_dropdown_destination, *convert_options)
format_menu_destination.grid(row=4, column=1, padx=10, pady=5)

# Progress Bar
progress_var = DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=20)

# Buttons for copying files
button_copy_files = Button(root, text="Copy Files", font=("Arial", 14), command=start_copy_process)
button_copy_files.pack(pady=10)

button_cancel = Button(root, text="Cancel", font=("Arial", 14), command=cancel_copy)
button_cancel.pack(pady=5)

root.mainloop()


# In[ ]:




