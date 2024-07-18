import tkinter as tk
from tkinter import filedialog, messagebox
from difflib import Differ
import os


file1 = []
file2 = []


def choose_file1():
    global file1
    file_path = filedialog.askopenfilename(filetypes=[("ASS files", "*.ass")])

    if file_path:
        file1_label.config(text=os.path.basename(file_path))

        with open(file_path, "r", encoding="utf-8") as f:
            file1 = f.readlines()


def choose_file2():
    global file2
    file_path = filedialog.askopenfilename(filetypes=[("ASS files", "*.ass")])

    if file_path:
        file2_label.config(text=os.path.basename(file_path))

        with open(file_path, "r", encoding="utf-8") as f:
            file2 = f.readlines()


def compare_events():
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)

        display_changes(file1, file2)

        result_text.config(state=tk.DISABLED)


def display_changes(file1, file2):
    try:
        file1_events_index = file1.index("[Events]\n")
        file2_events_index = file2.index("[Events]\n")
    except ValueError:
        result_text.insert(tk.END, "[Events] section not found in one or both files.")
        return

    events1 = file1[file1_events_index + 2:]
    events2 = file2[file2_events_index + 2:]

    text_to_compare1 = []
    text_to_compare2 = []

    max_length = max(len(events1), len(events2))

    for i in range(max_length):

        if i < len(events1):
            event1 = events1[i]
            format1 = event1.split(":", maxsplit=1)[0]
            event1_parts = event1.split(",", maxsplit=9)
            start1, end1, text1 = event1_parts[1], event1_parts[2], event1_parts[-1]

            if not event1_parts[3] == "TLmode":
                
                if format1 == "Comment":
                    format1 += " "

                text_to_compare1.append(f"{format1} {start1}, {end1}, {text1}")

        if i < len(events2):
            event2 = events2[i]
            format2 = event2.split(":", maxsplit=1)[0]
            event2_parts = event2.split(",", maxsplit=9)
            start2, end2, text2 = event2_parts[1], event2_parts[2], event2_parts[-1]

            if not event2_parts[3] == "TLmode":

                if format2 == "Comment":
                    format2 += " "

                text_to_compare2.append(f"{format2} {start2}, {end2}, {text2}")

    differ = Differ()
    diff = list(differ.compare(text_to_compare1, text_to_compare2))

    for line in diff:

        if line.startswith("+"):
            result_text.insert(tk.END, line, "green")

        elif line.startswith("-"):
            result_text.insert(tk.END, line, "red")

        elif not line.startswith("?"):
            result_text.insert(tk.END, line)


def save_changes_to_file():
    file_to_save = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

    if file_to_save:
        try:
            with open(file_to_save, "w", encoding="utf-8") as f:
                f.write(result_text.get("1.0", tk.END))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving changes to file: {str(e)}")


def switch_to_dark_mode():
    window.config(bg="black")
    file1_button.config(bg="gray", fg="white")
    file2_button.config(bg="gray", fg="white")
    compare_button.config(bg="gray", fg="white")
    result_text.config(bg="black", fg="white")
    result_text.tag_configure("red", background="#990000")
    result_text.tag_configure("green", background="#009900")
    buttons_frame.config(bg="black")
    file1_button_frame.config(bg="black")
    file2_button_frame.config(bg="black")
    compare_button_frame.config(bg="black")
    file1_label.config(bg="black", fg="white")
    file2_label.config(bg="black", fg="white")


def switch_to_light_mode():
    window.config(bg="white")
    file1_button.config(bg="lightgray", fg="black")
    file2_button.config(bg="lightgray", fg="black")
    compare_button.config(bg="lightgray", fg="black")
    result_text.config(bg="white", fg="black")
    result_text.tag_configure("red", background="#cc0000")
    result_text.tag_configure("green", background="#00cc00")
    buttons_frame.config(bg="white")
    file1_button_frame.config(bg="white")
    file2_button_frame.config(bg="white")
    compare_button_frame.config(bg="white")
    file1_label.config(bg="white", fg="black")
    file2_label.config(bg="white", fg="black")


# GUI
window = tk.Tk()
window.title("AegiChanges")
window.state("zoomed")
window.config(bg="black")


# Menu Bar
menu_bar = tk.Menu(window)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Save Changes to File", command=save_changes_to_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)

color_mode_menu = tk.Menu(menu_bar, tearoff=0)
color_mode_menu.add_command(label="Dark Mode", command=switch_to_dark_mode)
color_mode_menu.add_command(label="Light Mode", command=switch_to_light_mode)

menu_bar.add_cascade(label="File", menu=file_menu)
menu_bar.add_cascade(label="Color Mode", menu=color_mode_menu)

window.config(menu=menu_bar)


# Buttons
buttons_frame = tk.Frame(window, bg="black")
buttons_frame.pack(fill=tk.BOTH, padx=10, pady=10)

file1_button_frame = tk.Frame(buttons_frame, bg="black")
file1_button_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side="left")

file2_button_frame = tk.Frame(buttons_frame, bg="black")
file2_button_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side="left")

compare_button_frame = tk.Frame(buttons_frame, bg="black")
compare_button_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side="left")

file1_button = tk.Button(file1_button_frame, text="Choose old file", command=choose_file1, bg="gray", fg="white")
file1_button.pack(fill=tk.BOTH)
file1_label = tk.Label(file1_button_frame, bg="black", fg="white", width=30)
file1_label.pack(fill=tk.BOTH)

file2_button = tk.Button(file2_button_frame, text="Choose new file", command=choose_file2, bg="gray", fg="white")
file2_button.pack(fill=tk.BOTH)
file2_label = tk.Label(file2_button_frame, bg="black", fg="white", width=30)
file2_label.pack(fill=tk.BOTH)

compare_button = tk.Button(compare_button_frame, text="Compare Files", command=compare_events, bg="gray", fg="white", width=30)
compare_button.pack(fill=tk.BOTH)


# Result Text
scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_text = tk.Text(window, wrap=tk.WORD, bg="black", fg="white", yscrollcommand=scrollbar.set, state=tk.DISABLED)
result_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

scrollbar.config(command=result_text.yview)


# Tag Configuration
result_text.tag_configure("red", background="#990000")
result_text.tag_configure("green", background="#009900")

window.mainloop()
