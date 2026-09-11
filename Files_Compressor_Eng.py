"""
Name: Files Compressor with Encryption
Author: Sharan Kumar R (sharankumar-r)
Description: A desktop application to compress, encrypt, and extract files.
Combines zlib compression with Fernet (AES-128-CBC) symmetric encryption
for secure file archiving.
"""

import os
import ast
import zlib
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from cryptography.fernet import Fernet, InvalidToken


class SevenBLCompressor:
    def __init__(self, window):
        self.window = window
        self.window.title("Files Compressor with Encryption")
        self.window.geometry("560x640")
        self.window.minsize(500, 580)
        self.window.configure(bg="#f4f6f8")

        self.setup_styles()
        self.create_ui_elements()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TProgressbar", thickness=10)
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background="#2563eb",
            foreground="#ffffff",
            padding=6,
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8"), ("pressed", "#1e40af")],
        )

        self.style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 9),
            background="#e2e8f0",
            foreground="#1e293b",
            padding=5,
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#cbd5e1"), ("pressed", "#94a3b8")],
        )

    def create_ui_elements(self):
        main_frame = tk.Frame(self.window, bg="#f4f6f8", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(main_frame, bg="#f4f6f8")
        header_frame.pack(fill=tk.X, pady=(0, 12))

        title_label = tk.Label(
            header_frame,
            text="Files Compressor & Encryptor",
            font=("Segoe UI", 16, "bold"),
            bg="#f4f6f8",
            fg="#0f172a",
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Secure zlib compression with Fernet AES encryption (.7bl)",
            font=("Segoe UI", 9),
            bg="#f4f6f8",
            fg="#64748b",
        )
        subtitle_label.pack(anchor="w")

        # Section 1: Input files
        input_box = tk.LabelFrame(
            main_frame,
            text=" 1. Select Files ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#334155",
            padx=10,
            pady=8,
            relief=tk.GROOVE,
        )
        input_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        list_frame = tk.Frame(input_box, bg="#ffffff")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            font=("Consolas", 9),
            bg="#f8fafc",
            fg="#1e293b",
            selectbackground="#93c5fd",
            selectforeground="#0f172a",
            relief=tk.SOLID,
            bd=1,
            height=5,
        )
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        input_btn_frame = tk.Frame(input_box, bg="#ffffff")
        input_btn_frame.pack(fill=tk.X, pady=(6, 0))

        browse_input_btn = ttk.Button(
            input_btn_frame,
            text="Add Files...",
            style="Secondary.TButton",
            command=self.browse_input_files,
        )
        browse_input_btn.pack(side=tk.LEFT, padx=(0, 6))

        clear_files_btn = ttk.Button(
            input_btn_frame,
            text="Clear",
            style="Secondary.TButton",
            command=self.clear_files,
        )
        clear_files_btn.pack(side=tk.LEFT)

        # Section 2: Destination directory
        output_box = tk.LabelFrame(
            main_frame,
            text=" 2. Destination Folder ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#334155",
            padx=10,
            pady=8,
            relief=tk.GROOVE,
        )
        output_box.pack(fill=tk.X, pady=(0, 10))

        out_row = tk.Frame(output_box, bg="#ffffff")
        out_row.pack(fill=tk.X)

        self.output_entry = tk.Entry(
            out_row,
            font=("Segoe UI", 9),
            bg="#f8fafc",
            fg="#0f172a",
            relief=tk.SOLID,
            bd=1,
        )
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=3)

        browse_out_btn = ttk.Button(
            out_row,
            text="Browse...",
            style="Secondary.TButton",
            command=self.browse_output_directory,
        )
        browse_out_btn.pack(side=tk.RIGHT)

        # Section 3: Encryption Key
        key_box = tk.LabelFrame(
            main_frame,
            text=" 3. Encryption Key ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#334155",
            padx=10,
            pady=8,
            relief=tk.GROOVE,
        )
        key_box.pack(fill=tk.X, pady=(0, 10))

        key_row = tk.Frame(key_box, bg="#ffffff")
        key_row.pack(fill=tk.X)

        self.key_entry = tk.Entry(
            key_row,
            font=("Consolas", 9),
            bg="#f8fafc",
            fg="#0f172a",
            relief=tk.SOLID,
            bd=1,
        )
        self.key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=3)

        gen_key_btn = ttk.Button(
            key_row,
            text="Generate Key",
            style="Secondary.TButton",
            command=self.generate_and_set_key,
        )
        gen_key_btn.pack(side=tk.RIGHT)

        # Section 4: Progress & Actions
        action_frame = tk.Frame(main_frame, bg="#f4f6f8")
        action_frame.pack(fill=tk.X, pady=(4, 8))

        self.progress_bar = ttk.Progressbar(
            action_frame,
            orient="horizontal",
            mode="determinate",
            style="TProgressbar",
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        btn_row = tk.Frame(action_frame, bg="#f4f6f8")
        btn_row.pack(fill=tk.X)

        self.create_archive_button = ttk.Button(
            btn_row,
            text="Create Archive (.7bl)",
            style="Primary.TButton",
            command=self.on_create_archive_button_click,
        )
        self.create_archive_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.extract_archive_button = ttk.Button(
            btn_row,
            text="Extract Archive",
            style="Primary.TButton",
            command=self.on_extract_archive_button_click,
        )
        self.extract_archive_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Status footer
        self.result_label = tk.Label(
            main_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg="#f4f6f8",
            fg="#475569",
            anchor="w",
        )
        self.result_label.pack(fill=tk.X, pady=(4, 0))

    def browse_input_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select files to archive or extract",
            filetypes=[
                ("All Supported Files", "*.*"),
                ("7bl Archives", "*.7bl"),
            ],
        )
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.file_listbox.get(0, tk.END):
                    self.file_listbox.insert(tk.END, file_path)

    def clear_files(self):
        self.file_listbox.delete(0, tk.END)

    def browse_output_directory(self):
        directory_path = filedialog.askdirectory(title="Select Destination Directory")
        if directory_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory_path)

    def generate_key(self):
        return Fernet.generate_key()

    def generate_and_set_key(self):
        key = self.generate_key()
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, key.decode())
        self.update_status_message("Generated fresh Fernet encryption key.")

    def encrypt_data(self, data, key):
        fernet = Fernet(key)
        return fernet.encrypt(data)

    def decrypt_data(self, data, key):
        fernet = Fernet(key)
        return fernet.decrypt(data)

    def update_progress_bar(self, value):
        self.progress_bar["value"] = value
        self.window.update_idletasks()

    def update_status_message(self, message, is_error=False):
        self.result_label.config(
            text=message,
            fg="#dc2626" if is_error else "#16a34a" if "created" in message.lower() or "extracted" in message.lower() else "#475569",
        )
        self.window.update_idletasks()

    def create_archive(self, archive_file, files, key):
        archive_data = {}
        total = len(files)

        for i, file in enumerate(files):
            filename = os.path.basename(file)
            self.update_status_message(f"Compressing & encrypting: {filename} ({i+1}/{total})")
            with open(file, "rb") as infile:
                data = infile.read()
            compressed_data = zlib.compress(data, level=zlib.Z_BEST_COMPRESSION)
            encrypted_data = self.encrypt_data(compressed_data, key)
            archive_data[filename] = encrypted_data
            self.update_progress_bar(((i + 1) / total) * 90)

        with open(archive_file, "wb") as outfile:
            outfile.write(str(archive_data).encode("utf-8"))

        self.update_progress_bar(100)

    def extract_files_from_archive(self, archive_file, output_dir, key):
        with open(archive_file, "rb") as infile:
            raw_content = infile.read().decode("utf-8")

        # Safely evaluate literal dictionary without executing arbitrary code
        archive_data = ast.literal_eval(raw_content)

        if not isinstance(archive_data, dict):
            raise ValueError("Invalid archive format.")

        total_files = len(archive_data)
        for i, (filename, encrypted_data) in enumerate(archive_data.items()):
            self.update_status_message(f"Extracting: {filename} ({i+1}/{total_files})...")
            decrypted_data = self.decrypt_data(encrypted_data, key)
            decompressed_data = zlib.decompress(decrypted_data)

            output_file = os.path.join(output_dir, filename)
            with open(output_file, "wb") as outfile:
                outfile.write(decompressed_data)

            self.update_progress_bar(((i + 1) / total_files) * 100)

    def on_create_archive_button_click(self):
        input_files = list(self.file_listbox.get(0, tk.END))
        output_dir = self.output_entry.get().strip()
        key_str = self.key_entry.get().strip()

        if not input_files:
            self.update_status_message("Select at least one file to archive.", is_error=True)
            return

        if not output_dir:
            self.update_status_message("Select a destination directory.", is_error=True)
            return

        if not key_str:
            self.update_status_message("Enter or generate an encryption key.", is_error=True)
            return

        key = key_str.encode()

        for input_file in input_files:
            if not os.path.isfile(input_file):
                self.update_status_message(f"File not found: {input_file}", is_error=True)
                return

        try:
            archive_file = os.path.join(output_dir, "archived_data.7bl")
            self.create_archive(archive_file, input_files, key)
            self.update_status_message(f"Archive saved to {archive_file}!")
        except Exception as e:
            traceback.print_exc()
            self.update_progress_bar(0)
            self.update_status_message(f"Archive creation failed: {e}", is_error=True)

    def on_extract_archive_button_click(self):
        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            archive_file = self.file_listbox.get(selected_indices[0])
        elif self.file_listbox.size() > 0:
            archive_file = self.file_listbox.get(0)
        else:
            self.update_status_message("Select an archive (.7bl) from the list.", is_error=True)
            return

        output_dir = self.output_entry.get().strip()
        key_str = self.key_entry.get().strip()

        if not output_dir:
            self.update_status_message("Select an extraction directory.", is_error=True)
            return

        if not key_str:
            self.update_status_message("Enter the encryption key.", is_error=True)
            return

        if not os.path.isfile(archive_file):
            self.update_status_message(f"Archive file not found: {archive_file}", is_error=True)
            return

        os.makedirs(output_dir, exist_ok=True)
        key = key_str.encode()

        try:
            self.extract_files_from_archive(archive_file, output_dir, key)
            self.update_status_message(f"Successfully extracted to {output_dir}!")
        except InvalidToken:
            self.update_progress_bar(0)
            self.update_status_message("Decryption failed: Incorrect encryption key.", is_error=True)
        except Exception as e:
            traceback.print_exc()
            self.update_progress_bar(0)
            self.update_status_message(f"Extraction failed: {e}", is_error=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = SevenBLCompressor(root)
    root.mainloop()
