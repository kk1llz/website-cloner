import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk

visited = set()



def clean_filename(url):
    path = urlparse(url).path.strip("/")
    if not path:
        return "index"
    return path.replace("/", "_").replace("\\", "_")

def save_html(url, content, folder, log):
    filename = clean_filename(url) + ".html"
    full_path = os.path.join(folder, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    log.insert(tk.END, f"[SAVED] {full_path}\n")
    log.see(tk.END)

def save_binary(url, content, folder, log):
    filename = clean_filename(url)
    full_path = os.path.join(folder, filename)
    with open(full_path, "wb") as f:
        f.write(content)
    log.insert(tk.END, f"[SAVED] {full_path}\n")
    log.see(tk.END)

def download(url, folder, log):
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        log.insert(tk.END, f"[ERROR] {url}: {e}\n")
        log.see(tk.END)
        return

    content_type = response.headers.get("Content-Type", "")

    if "text/html" not in content_type:
        save_binary(url, response.content, folder, log)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    save_html(url, response.text, folder, log)

    for tag in soup.find_all(["a", "img", "link", "script"]):
        attr = "href" if tag.name in ["a", "link"] else "src"
        link = tag.get(attr)

        if not link:
            continue

        absolute = urljoin(url, link)
        domain = urlparse(url).netloc

        if urlparse(absolute).netloc == domain:
            download(absolute, folder, log)


def choose_folder():
    path = filedialog.askdirectory()
    if path:
        folder_var.set(path)

def start_download():
    url = url_entry.get().strip()
    folder = folder_var.get().strip()
    log.delete(1.0, tk.END)

    if not url:
        log.insert(tk.END, "Enter a URL first.\n")
        return
    if not folder:
        log.insert(tk.END, "Choose a destination folder.\n")
        return

    visited.clear()
    log.insert(tk.END, f"Starting download...\nURL: {url}\nDestination: {folder}\n\n")
    download(url, folder, log)
    log.insert(tk.END, "\nDone.\n")


image_path = "fsociety.png"
def load_local_image(path, max_width=500):
    try:
        img = Image.open(path)
        w_percent = max_width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)  # Updated to LANCZOS
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None



root = tk.Tk()
root.title("Website Cloner")
root.geometry("650x600")
root.configure(bg="black")


photo = load_local_image(image_path)
if photo:
    img_label = tk.Label(root, image=photo, bg="black")
    img_label.pack(pady=5)


title = tk.Label(
    root,
    text="Website Cloner",
    font=("Arial", 22, "bold"),
    bg="black",
    fg="red"
)
title.pack(pady=5)


frame = tk.Frame(root, bg="black")
frame.pack(pady=10)

tk.Label(frame, text="Website URL:", bg="black", fg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
url_entry = tk.Entry(frame, width=50, bg="#222", fg="red", insertbackground="red")
url_entry.grid(row=0, column=1, padx=10)

tk.Label(frame, text="Save To Folder:", bg="black", fg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
folder_var = tk.StringVar()
folder_entry = tk.Entry(frame, width=40, textvariable=folder_var, bg="#222", fg="red", insertbackground="red")
folder_entry.grid(row=1, column=1, padx=10)

browse_btn = tk.Button(frame, text="Browse", bg="red", fg="white", command=choose_folder)
browse_btn.grid(row=1, column=2)


start_btn = tk.Button(root, text="Start Archiving", bg="red", fg="white", font=("Arial", 12, "bold"), command=start_download)
start_btn.pack(pady=10)


log = scrolledtext.ScrolledText(root, width=70, height=15, bg="#111", fg="white", insertbackground="white")
log.pack(pady=10)

root.mainloop()

