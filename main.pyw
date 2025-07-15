# /main/headx_presence_xt_enhanced.py
# made by headx / the psychon 🔥
# Enhanced version with profiles, validation, and better error handling

import sys
import subprocess
import importlib
import os
import time
import json
import threading
from datetime import datetime

def ensure_package(pkg, pip_name=None):
    try:
        importlib.import_module(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name or pkg])
    else:
        # Try to upgrade if not latest
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', pip_name or pkg])
        except Exception:
            pass

ensure_package('pypresence')
ensure_package('PIL', 'pillow')
ensure_package('pystray')

from pypresence import Presence
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from PIL import Image, ImageTk
import pystray

CLIENT_ID = "123456789012345678"  # ⚠️ Replace with your actual Discord App Client ID!
PROFILES_FILE = "profiles.json"

class DiscordPresenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("headxPresence XT - Discord Activity Maker")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Initialize variables
        self.rpc = None
        self.running = False
        self.animate = False
        self.profiles = self.load_profiles()
        self.start_time = 0
        
        # Image references for preview
        self._preview_large_img = None
        self._preview_small_img = None
        
        self.setup_ui()
        self.setup_tray_icon()
        
        # Auto-connect after UI setup
        self.root.after(100, self.auto_connect_to_discord)
        
        # Hide to tray on close
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def setup_tray_icon(self):
        try:
            # Create tray icon with Pillow image
            icon_img = Image.new('RGB', (64, 64), color=(44, 47, 58))
            self.tray_icon = pystray.Icon(
                "headxPresenceXT", 
                icon_img, 
                "headxPresence XT", 
                menu=pystray.Menu(
                    pystray.MenuItem('Öffnen', self.show_window),
                    pystray.MenuItem('Beenden', self.quit_app)
                )
            )
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Tray icon setup failed: {e}")

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon=None, item=None):
        self.running = False
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except:
                pass
        self.root.after(0, self.root.destroy)

    def hide_window(self):
        self.root.withdraw()

    def auto_connect_to_discord(self):
        # Try to connect to Discord automatically on app start
        try:
            client_id = self.client_id_var.get() if hasattr(self, 'client_id_var') else "1394628981843693659"
            self.rpc = Presence(client_id)
            self.rpc.connect()
            self.log_message("Automatisch mit Discord verbunden.")
        except Exception as e:
            self.log_message(f"Automatische Verbindung zu Discord fehlgeschlagen: {e}")
        
    def setup_ui(self):
        # Modern dark theme
        self.root.tk_setPalette(
            background="#23272A", 
            foreground="#FFFFFF", 
            activeBackground="#2C2F33", 
            activeForeground="#7289DA"
        )

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#23272A")
        style.configure("TLabel", background="#23272A", foreground="#FFFFFF")
        style.configure("TButton", background="#7289DA", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#2C2F33", foreground="#FFFFFF")
        style.configure("TCombobox", fieldbackground="#2C2F33", foreground="#FFFFFF")
        style.configure("TCheckbutton", background="#23272A", foreground="#FFFFFF")
        style.configure("TLabelframe", background="#23272A", foreground="#7289DA", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background="#23272A", foreground="#7289DA", font=("Segoe UI", 10, "bold"))
        style.configure("Card.TFrame", background="#2C2F33", relief="solid", borderwidth=1)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, 
            text="headxPresence XT", 
            font=("Segoe UI", 18, "bold"), 
            foreground="#7289DA", 
            background="#23272A"
        )
        title_label.pack(pady=(0, 10))

        # Profile management
        profile_frame = ttk.LabelFrame(main_frame, text="Profile", padding="5")
        profile_frame.pack(fill=tk.X, pady=(0, 10))

        profile_inner = ttk.Frame(profile_frame)
        profile_inner.pack(fill=tk.X)

        ttk.Label(profile_inner, text="Profil:").pack(side=tk.LEFT)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_inner, textvariable=self.profile_var, width=15)
        self.profile_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.profile_combo.bind('<<ComboboxSelected>>', self.load_profile)

        ttk.Button(profile_inner, text="Speichern", command=self.save_profile).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(profile_inner, text="Löschen", command=self.delete_profile).pack(side=tk.LEFT, padx=(5, 0))

        self.update_profile_combo()

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Rich Presence Einstellungen", padding="5")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Client ID
        client_frame = ttk.Frame(settings_frame)
        client_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(client_frame, text="Client ID:").pack(side=tk.LEFT)
        self.client_id_var = tk.StringVar(value="1394628981843693659")
        client_entry = ttk.Entry(client_frame, textvariable=self.client_id_var, width=30)
        client_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Title
        title_frame = ttk.Frame(settings_frame)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(title_frame, text="Titel:").pack(side=tk.LEFT)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=self.title_var, width=40)
        title_entry.pack(side=tk.LEFT, padx=(5, 0))
        title_entry.bind('<KeyRelease>', lambda e: self.update_preview())

        # Description
        desc_frame = ttk.Frame(settings_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(desc_frame, text="Beschreibung:").pack(side=tk.LEFT)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var, width=40)
        desc_entry.pack(side=tk.LEFT, padx=(5, 0))
        desc_entry.bind('<KeyRelease>', lambda e: self.update_preview())

        # Image settings
        image_frame = ttk.Frame(settings_frame)
        image_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(image_frame, text="Bild-Key:").pack(side=tk.LEFT)
        self.image_var = tk.StringVar()
        image_entry = ttk.Entry(image_frame, textvariable=self.image_var, width=30)
        image_entry.pack(side=tk.LEFT, padx=(5, 0))
        image_entry.bind('<KeyRelease>', lambda e: self.update_preview())

        ttk.Button(image_frame, text="Datei wählen", command=self.choose_large_image).pack(side=tk.LEFT, padx=(5, 0))
        self.large_image_preview = ttk.Label(image_frame, text="", width=10)
        self.large_image_preview.pack(side=tk.LEFT, padx=(5, 0))

        # Small image
        small_image_frame = ttk.Frame(settings_frame)
        small_image_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(small_image_frame, text="Kleines Bild:").pack(side=tk.LEFT)
        self.small_image_var = tk.StringVar()
        small_image_entry = ttk.Entry(small_image_frame, textvariable=self.small_image_var, width=30)
        small_image_entry.pack(side=tk.LEFT, padx=(5, 0))
        small_image_entry.bind('<KeyRelease>', lambda e: self.update_preview())

        ttk.Button(small_image_frame, text="Datei wählen", command=self.choose_small_image).pack(side=tk.LEFT, padx=(5, 0))
        self.small_image_preview = ttk.Label(small_image_frame, text="", width=10)
        self.small_image_preview.pack(side=tk.LEFT, padx=(5, 0))

        # --- DYNAMIC BUTTONS SECTION ---
        button_section = ttk.LabelFrame(main_frame, text="Benutzerdefinierte Buttons", padding="5")
        button_section.pack(fill=tk.X, pady=(0, 10))

        self.custom_buttons = []  # List of dicts: {frame, button, func_var, config_frame}
        self.available_functions = {
            "Nichts": None,
            "Öffne Webseite": self.button_action_open_url,
            "Zeige Nachricht": self.button_action_show_message,
            # Add more functions here as needed
        }

        add_btn = ttk.Button(button_section, text="Button hinzufügen", command=self.add_custom_button)
        add_btn.pack(anchor=tk.W, pady=(0, 5))

        self.buttons_container = ttk.Frame(button_section)
        self.buttons_container.pack(fill=tk.X)

        # --- END DYNAMIC BUTTONS SECTION ---

        # Discord Style Activity Preview
        preview_label = ttk.Label(
            main_frame, 
            text="Discord Activity Vorschau", 
            font=("Segoe UI", 10, "bold"), 
            foreground="#7289DA", 
            background="#23272A"
        )
        preview_label.pack(anchor=tk.W, pady=(10, 0))

        self.discord_card = self.build_discord_style_activity(main_frame)

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Optionen", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.use_timer = tk.BooleanVar()
        timer_check = ttk.Checkbutton(options_frame, text="Timer anzeigen (seit Start)", variable=self.use_timer)
        timer_check.pack(anchor=tk.W)
        timer_check.bind('<Button-1>', lambda e: self.root.after(10, self.update_preview))

        self.use_anim = tk.BooleanVar()
        anim_check = ttk.Checkbutton(options_frame, text="Titel mit Schreibanimation", variable=self.use_anim)
        anim_check.pack(anchor=tk.W)

        # Animation speed
        speed_frame = ttk.Frame(options_frame)
        speed_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(speed_frame, text="Animationsgeschwindigkeit:").pack(side=tk.LEFT)
        self.anim_speed = tk.DoubleVar(value=0.2)
        speed_scale = ttk.Scale(speed_frame, from_=0.1, to=1.0, variable=self.anim_speed, orient=tk.HORIZONTAL)
        speed_scale.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Status and runtime
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="Status: Inaktiv", foreground="#F04747")
        self.status_label.pack(side=tk.LEFT)

        self.runtime_label = ttk.Label(status_frame, text="Laufzeit: 00:00:00")
        self.runtime_label.pack(side=tk.RIGHT)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = tk.Button(
            control_frame, 
            text="Start", 
            command=self.start_presence, 
            bg="#43B581", 
            fg="#FFFFFF", 
            font=("Segoe UI", 10, "bold"), 
            relief="flat", 
            activebackground="#3BA55D", 
            activeforeground="#FFFFFF", 
            width=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = tk.Button(
            control_frame, 
            text="Stop", 
            command=self.stop_presence, 
            bg="#F04747", 
            fg="#FFFFFF", 
            font=("Segoe UI", 10, "bold"), 
            relief="flat", 
            activebackground="#992D22", 
            activeforeground="#FFFFFF", 
            width=10, 
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Bind Enter key to start button
        self.root.bind('<Return>', lambda event: self.start_btn.invoke() if self.start_btn['state'] == tk.NORMAL else None)

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=6, 
            bg="#2C2F33", 
            fg="#FFFFFF", 
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.update_start_stop_buttons()

    def add_custom_button(self):
        # Frame for this button row
        row = ttk.Frame(self.buttons_container)
        row.pack(fill=tk.X, pady=2)

        # Button label
        btn = ttk.Button(row, text="Button", width=10)
        btn.pack(side=tk.LEFT, padx=(0, 5))

        # Dropdown for function selection
        func_var = tk.StringVar(value="Nichts")
        func_dropdown = ttk.Combobox(row, textvariable=func_var, values=list(self.available_functions.keys()), width=18, state="readonly")
        func_dropdown.pack(side=tk.LEFT, padx=(0, 5))

        # Config frame (for function-specific options)
        config_frame = ttk.Frame(row)
        config_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Remove button
        remove_btn = ttk.Button(row, text="Entfernen", command=lambda: self.remove_custom_button(row))
        remove_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Store in list
        self.custom_buttons.append({
            "frame": row,
            "button": btn,
            "func_var": func_var,
            "config_frame": config_frame,
            "func_dropdown": func_dropdown
        })

        # Bind function selection
        func_dropdown.bind('<<ComboboxSelected>>', lambda e, fr=config_frame, v=func_var: self.update_button_config(fr, v))

        # Initial config
        self.update_button_config(config_frame, func_var)

    def remove_custom_button(self, row):
        for btn in self.custom_buttons:
            if btn["frame"] == row:
                btn["frame"].destroy()
                self.custom_buttons.remove(btn)
                break

    def update_button_config(self, config_frame, func_var):
        # Clear previous config widgets
        for widget in config_frame.winfo_children():
            widget.destroy()

        func = func_var.get()
        if func == "Öffne Webseite":
            tk.Label(config_frame, text="URL:", bg="#23272A", fg="#FFFFFF").pack(side=tk.LEFT)
            url_var = tk.StringVar()
            url_entry = ttk.Entry(config_frame, textvariable=url_var, width=25)
            url_entry.pack(side=tk.LEFT, padx=(5, 0))
            config_frame.url_var = url_var  # Attach for later use
        elif func == "Zeige Nachricht":
            tk.Label(config_frame, text="Text:", bg="#23272A", fg="#FFFFFF").pack(side=tk.LEFT)
            msg_var = tk.StringVar()
            msg_entry = ttk.Entry(config_frame, textvariable=msg_var, width=25)
            msg_entry.pack(side=tk.LEFT, padx=(5, 0))
            config_frame.msg_var = msg_var
        # Add more function configs as needed

    def button_action_open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def button_action_show_message(self, msg):
        messagebox.showinfo("Nachricht", msg)

    def build_discord_style_activity(self, parent):
        # Discord Activity Card Lookalike
        card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        card.pack(fill=tk.X, pady=(10, 0))
        
        # Top: Large image left, text right
        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill=tk.X)
        
        self.card_large_img = tk.Label(
            top, 
            text="[Großes Bild]", 
            width=10, 
            height=5, 
            bg="#23272A", 
            fg="#99AAB5", 
            relief="groove"
        )
        self.card_large_img.pack(side=tk.LEFT, padx=(0, 10))
        
        textblock = ttk.Frame(top, style="Card.TFrame")
        textblock.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.card_title = tk.Label(
            textblock, 
            text="", 
            font=("Segoe UI", 12, "bold"), 
            bg="#2C2F33", 
            fg="#FFFFFF", 
            anchor="w"
        )
        self.card_title.pack(anchor="w", fill=tk.X)
        
        self.card_desc = tk.Label(
            textblock, 
            text="", 
            font=("Segoe UI", 10), 
            bg="#2C2F33", 
            fg="#B9BBBE", 
            anchor="w"
        )
        self.card_desc.pack(anchor="w", fill=tk.X)
        
        # Bottom: Small image and timer
        bottom = ttk.Frame(card, style="Card.TFrame")
        bottom.pack(fill=tk.X, pady=(5, 0))
        
        self.card_small_img = tk.Label(
            bottom, 
            text="[Kleines Bild]", 
            width=5, 
            height=2, 
            bg="#23272A", 
            fg="#99AAB5", 
            relief="groove"
        )
        self.card_small_img.pack(side=tk.LEFT)
        
        self.card_timer = tk.Label(
            bottom, 
            text="", 
            font=("Segoe UI", 8), 
            bg="#2C2F33", 
            fg="#43B581"
        )
        self.card_timer.pack(side=tk.LEFT, padx=(10, 0))
        
        return card

    def update_start_stop_buttons(self):
        if self.running:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def choose_large_image(self):
        file_path = filedialog.askopenfilename(
            title="Großes Bild auswählen", 
            filetypes=[("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.image_var.set(file_path)
            self.large_image_preview.config(text=os.path.basename(file_path))
            self.update_preview()

    def choose_small_image(self):
        file_path = filedialog.askopenfilename(
            title="Kleines Bild auswählen", 
            filetypes=[("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.small_image_var.set(file_path)
            self.small_image_preview.config(text=os.path.basename(file_path))
            self.update_preview()

    def update_preview(self):
        # Update Discord-style preview card
        title = self.title_var.get()
        desc = self.desc_var.get()
        self.card_title.config(text=title if title else "Kein Titel")
        self.card_desc.config(text=desc if desc else "Keine Beschreibung")
        
        # Large image preview
        large_img_path = self.image_var.get()
        if large_img_path and os.path.isfile(large_img_path):
            try:
                img = Image.open(large_img_path).resize((80, 80))
                self._preview_large_img = ImageTk.PhotoImage(img)
                self.card_large_img.config(image=self._preview_large_img, text="")
            except Exception:
                self.card_large_img.config(image="", text=os.path.basename(large_img_path))
        else:
            self.card_large_img.config(image="", text="[Großes Bild]")
        
        # Small image preview
        small_img_path = self.small_image_var.get()
        if small_img_path and os.path.isfile(small_img_path):
            try:
                img = Image.open(small_img_path).resize((40, 40))
                self._preview_small_img = ImageTk.PhotoImage(img)
                self.card_small_img.config(image=self._preview_small_img, text="")
            except Exception:
                self.card_small_img.config(image="", text=os.path.basename(small_img_path))
        else:
            self.card_small_img.config(image="", text="[Kleines Bild]")
        
        # Timer
        if self.use_timer.get():
            self.card_timer.config(text="seit " + datetime.now().strftime("%H:%M"))
        else:
            self.card_timer.config(text="")

    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.client_id_var.get() or self.client_id_var.get() == "123456789012345678":
            messagebox.showerror("Fehler", "Bitte gültige Client-ID eintragen!")
            return False
            
        if not self.title_var.get().strip():
            messagebox.showerror("Fehler", "Titel darf nicht leer sein!")
            return False
            
        return True
        
    def start_presence(self):
        if not self.validate_inputs():
            return
            
        try:
            if self.rpc:
                try:
                    self.rpc.close()
                except:
                    pass
                    
            self.rpc = Presence(self.client_id_var.get())
            self.rpc.connect()
            self.running = True
            self.start_time = time.time()
            self.status_label.config(text="Status: Aktiv", foreground="#43B581")
            self.update_start_stop_buttons()
            self.log_message("Rich Presence gestartet")
            
            # Start presence update thread
            t = threading.Thread(target=self.update_presence)
            t.daemon = True
            t.start()
            
            # Start runtime counter
            self.update_runtime()
            
        except Exception as e:
            self.log_message(f"Fehler beim Starten: {e}")
            messagebox.showerror("Fehler", f"Discord-Fehler: {e}")
            
    def stop_presence(self):
        self.running = False
        self.status_label.config(text="Status: Inaktiv", foreground="#F04747")
        self.update_start_stop_buttons()
        
        try:
            if self.rpc:
                self.rpc.clear()
                self.rpc.close()
                self.log_message("Rich Presence gestoppt")
        except Exception as e:
            self.log_message(f"Fehler beim Stoppen: {e}")
            
    def update_runtime(self):
        if self.running:
            runtime = int(time.time() - self.start_time)
            hours = runtime // 3600
            minutes = (runtime % 3600) // 60
            seconds = runtime % 60
            self.runtime_label.config(text=f"Laufzeit: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_runtime)
            
    def update_presence(self):
        start = int(time.time())
        base_title = self.title_var.get()
        
        while self.running:
            try:
                if self.use_anim.get():
                    # Typing animation
                    for i in range(len(base_title) + 1):
                        if not self.running:
                            return
                        title = base_title[:i] + "|" if i < len(base_title) else base_title
                        self.send_presence(title, start)
                        time.sleep(self.anim_speed.get())
                    
                    # Pause before repeating
                    time.sleep(2)
                else:
                    self.send_presence(base_title, start)
                    time.sleep(15)
                    
            except Exception as e:
                self.log_message(f"Fehler beim Update: {e}")
                time.sleep(5)
                
    def send_presence(self, title, start):
        try:
            payload = {
                "state": self.desc_var.get(),
                "details": title,
                "large_text": "headxPresence XT 🔥"
            }
            
            # Handle images
            large_img = self.image_var.get()
            if large_img:
                if os.path.isfile(large_img):
                    # If it's a file path, use filename as key
                    payload["large_image"] = os.path.splitext(os.path.basename(large_img))[0]
                else:
                    # If it's already a key, use it directly
                    payload["large_image"] = large_img
            
            small_img = self.small_image_var.get()
            if small_img:
                if os.path.isfile(small_img):
                    payload["small_image"] = os.path.splitext(os.path.basename(small_img))[0]
                else:
                    payload["small_image"] = small_img
                payload["small_text"] = "by headx"
                
            if self.use_timer.get():
                payload["start"] = start
                
            self.rpc.update(**payload)
            
        except Exception as e:
            self.log_message(f"Fehler beim Senden: {e}")
            
    def load_profiles(self):
        try:
            if os.path.exists(PROFILES_FILE):
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profiles: {e}")
        return {}
        
    def save_profiles(self):
        try:
            with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_message(f"Fehler beim Speichern: {e}")
            
    def update_profile_combo(self):
        self.profile_combo['values'] = list(self.profiles.keys())
        
    def save_profile(self):
        name = self.profile_var.get().strip()
        if not name:
            messagebox.showerror("Fehler", "Bitte Profilname eingeben!")
            return
            
        profile_data = {
            "client_id": self.client_id_var.get(),
            "title": self.title_var.get(),
            "description": self.desc_var.get(),
            "image": self.image_var.get(),
            "small_image": self.small_image_var.get(),
            "use_timer": self.use_timer.get(),
            "use_animation": self.use_anim.get(),
            "animation_speed": self.anim_speed.get()
        }
        
        self.profiles[name] = profile_data
        self.save_profiles()
        self.update_profile_combo()
        self.log_message(f"Profil '{name}' gespeichert")
        
    def load_profile(self, event=None):
        name = self.profile_var.get()
        if name in self.profiles:
            data = self.profiles[name]
            self.client_id_var.set(data.get("client_id", ""))
            self.title_var.set(data.get("title", ""))
            self.desc_var.set(data.get("description", ""))
            self.image_var.set(data.get("image", ""))
            self.small_image_var.set(data.get("small_image", ""))
            self.use_timer.set(data.get("use_timer", False))
            self.use_anim.set(data.get("use_animation", False))
            self.anim_speed.set(data.get("animation_speed", 0.2))
            self.update_preview()
            self.log_message(f"Profil '{name}' geladen")
            
    def delete_profile(self):
        name = self.profile_var.get()
        if name in self.profiles:
            if messagebox.askyesno("Bestätigung", f"Profil '{name}' wirklich löschen?"):
                del self.profiles[name]
                self.save_profiles()
                self.update_profile_combo()
                self.profile_var.set("")
                self.log_message(f"Profil '{name}' gelöscht")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscordPresenceApp(root)
    root.mainloop()