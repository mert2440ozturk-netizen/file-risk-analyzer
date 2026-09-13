import tkinter as tk # Arayüz oluşturmak için Tkinter’ı yükler; kısaca tk adıyla kullanırız.

from tkinter import filedialog
from pathlib import Path

def select_file():
    file_path = filedialog.askopenfilename(
        title="incelenecek dosyayı seç",
        parent=window,
    )

    if not file_path:
        return

    file_name = Path(file_path).name
    selected_file_label.config(text=f"Seçilen dosya: {file_name}")

window = tk.Tk() # Ana pencereyi oluşturur.
window.title("Dosya risk analizörü")
window.geometry("800x500")  # Başlangıç genişliğini ve yüksekliğini piksel olarak belirler.
window.minsize(600,400) # Pencerenin küçültülebileceği en küçük boyutu belirler.
window.configure(bg="#111827")

title_label = tk.Label(
    window,
    text="Dosya risk analizörü",
    font=("Segoe UI", 24, "bold"),
    bg="#111827",
    fg="#F9FAFB"
)
title_label.pack(pady=(60,15))

description_label = tk.Label(
    window,
    text="Dosyaları incele, risk işaretlerini öğren.",
    font=("Segoe UI", 12),
    bg="#111827",
    fg="#9CA3AF",
)
description_label.pack()

select_button = tk.Button(
    window,
    text="dosya seç",
    command= select_file,
    bg="#2563EB",
    fg="#FFFFFF",
    padx=24,
    pady=12,
    cursor="hand2",
)
select_button.pack(pady=(35,20))

selected_file_label = tk.Label(
    window,
    text="henüz dosya seçilmedi",
    font=("Segoe UI", 12, "bold"),
    bg="#2563EB",
    fg="#FFFFFF",
    wraplength=550,
)
selected_file_label.pack(padx=20)

window.mainloop()