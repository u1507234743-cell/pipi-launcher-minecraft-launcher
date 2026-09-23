import os
import sys
import shutil
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import minecraft_launcher_lib

class PipiLauncherV4:
    def __init__(self, root):
        self.root = root
        self.root.title("Pipi Launcher v4.0 - Auto Java & Console")
        self.root.geometry("850x620")
        self.root.configure(bg="#0F1015")
        self.root.resizable(False, False)

        self.mc_dir = minecraft_launcher_lib.utils.get_minecraft_directory()
        self.versions = ["1.20.1", "1.19.4", "1.16.5", "1.12.2", "1.8.9"]

        self.create_ui()

    def create_ui(self):
        # Nagłówek
        header = tk.Frame(self.root, bg="#161722", height=70)
        header.pack(fill="x", side="top")
        tk.Label(header, text="🚀 PIPI LAUNCHER", font=("Impact", 24), fg="#00E5FF", bg="#161722").pack(side="left", padx=20, pady=10)
        tk.Label(header, text="AUTO-JAVA MOJANG EDITION", font=("Consolas", 9, "bold"), fg="#6C7293", bg="#161722").pack(side="left", pady=18)

        # Panel Główny
        main_frame = tk.Frame(self.root, bg="#0F1015")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Ustawienia (Góra)
        settings_card = tk.Frame(main_frame, bg="#181924", bd=1, relief="solid")
        settings_card.place(x=0, y=0, width=810, height=180)

        tk.Label(settings_card, text="Nick gracza:", font=("Arial", 10, "bold"), fg="#A0A5C0", bg="#181924").grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        self.nick_entry = tk.Entry(settings_card, font=("Arial", 11), bg="#10111A", fg="#00E5FF", insertbackground="white", bd=0, width=30)
        self.nick_entry.grid(row=1, column=0, padx=20, pady=(0, 15), ipady=5)
        self.nick_entry.insert(0, "Gracz_Pipi")

        tk.Label(settings_card, text="Wersja Minecrafta:", font=("Arial", 10, "bold"), fg="#A0A5C0", bg="#181924").grid(row=0, column=1, padx=20, pady=(15, 5), sticky="w")
        self.version_combo = ttk.Combobox(settings_card, values=self.versions, state="readonly", font=("Arial", 10), width=25)
        self.version_combo.grid(row=1, column=1, padx=20, pady=(0, 15), ipady=3)
        self.version_combo.current(0)

        # RAM
        tk.Label(settings_card, text="Pamięć RAM:", font=("Arial", 10, "bold"), fg="#A0A5C0", bg="#181924").grid(row=2, column=0, padx=20, sticky="w")
        self.ram_slider = tk.Scale(settings_card, from_=2, to=12, orient="horizontal", bg="#181924", fg="#FFFFFF", highlightthickness=0, width=12, length=200)
        self.ram_slider.set(4)
        self.ram_slider.grid(row=3, column=0, padx=20, pady=(0, 10))

        # Okno Logów / Konsoli (Dół)
        log_label = tk.Label(main_frame, text="KONSOLA I LOGI URUCHAMIANIA:", font=("Arial", 9, "bold"), fg="#6C7293", bg="#0F1015")
        log_label.place(x=0, y=190)

        self.log_box = tk.Text(main_frame, bg="#0A0B10", fg="#00FF88", font=("Consolas", 9), bd=1, relief="solid")
        self.log_box.place(x=0, y=215, width=810, height=210)

        # Dolny pasek
        bottom_frame = tk.Frame(self.root, bg="#161722", height=80)
        bottom_frame.pack(fill="x", side="bottom")

        self.status_label = tk.Label(bottom_frame, text="Gotowy.", font=("Arial", 10), fg="#A0A5C0", bg="#161722")
        self.status_label.pack(side="left", padx=20)

        self.play_btn = tk.Button(
            bottom_frame, text="GRAJ TERAZ", font=("Impact", 18), bg="#00E5FF", fg="#0F1015", bd=0, cursor="hand2", command=self.start_process
        )
        self.play_btn.pack(side="right", padx=20, pady=15, ipadx=25, ipady=5)

    def log(self, text):
        """ Wypisuje tekst w konsoli wewnątrz oknem """
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)
        self.status_label.config(text=text)

    def find_or_install_java(self):
        """ Szuka Javy w systemie, a jeśli brak - pobiera oficjalną od Mojanga """
        # 1. Sprawdź systemowy PATH
        system_java = shutil.which("javaw") or shutil.which("java")
        if system_java:
            self.log(f"[JAVA] Znaleziono Javę w systemie: {system_java}")
            return system_java

        # 2. Sprawdź domyślną Javę Mojanga w folderze .minecraft
        mojang_java = os.path.join(self.mc_dir, "runtime", "java-runtime-gamma", "windows-x64", "java-runtime-gamma", "bin", "javaw.exe")
        if os.path.exists(mojang_java):
            self.log(f"[JAVA] Znaleziono Jave Mojanga: {mojang_java}")
            return mojang_java

        # 3. Jeśli brak, pobierz oficjalną Javę Mojanga przez minecraft-launcher-lib
        self.log("[JAVA] Brak Javy na komputerze! Pobieranie oficjalnej Javy od Mojanga...")
        try:
            minecraft_launcher_lib.runtime.install_jvm_runtime("java-runtime-gamma", self.mc_dir)
            if os.path.exists(mojang_java):
                self.log("[JAVA] Pomyślnie pobrano i zainstalowano Javę!")
                return mojang_java
        except Exception as e:
            self.log(f"[BŁĄD JAVA] Nie udało się pobrać automatycznie: {e}")

        return None

    def start_process(self):
        nick = self.nick_entry.get().strip()
        version = self.version_combo.get()
        ram = self.ram_slider.get()

        if not nick:
            messagebox.showwarning("Błąd", "Wpisz nick!")
            return

        self.play_btn.config(state="disabled", bg="#333344", text="PRACUJĘ...")
        self.log_box.delete("1.0", tk.END)
        threading.Thread(target=self._launch_thread, args=(nick, version, ram), daemon=True).start()

    def _launch_thread(self, nick, version, ram):
        try:
            self.log(f"=== ROZPOCZYNANIE URUCHAMIANIA DLA: {nick} ===")

            # 1. Sprawdzanie / Pobieranie Javy
            java_executable = self.find_or_install_java()

            # 2. Pobieranie plików Minecrafta
            self.log(f"[MINECRAFT] Pobieranie / Weryfikacja wersji {version}...")
            callback = {
                "setStatus": lambda status: self.log(f"[POBIERANIE] {status}"),
                "setProgress": lambda v: None,
                "setMax": lambda v: None
            }
            minecraft_launcher_lib.install.install_minecraft_version(version, self.mc_dir, callback=callback)

            # 3. Konfiguracja parametrów
            options = {
                "username": nick,
                "uuid": "",
                "token": "",
                "jvmArguments": [f"-Xmx{ram}G", "-Xms2G"]
            }

            if java_executable:
                options["executablePath"] = java_executable

            # 4. Generowanie komendy i start
            self.log("[START] Generowanie komendy startowej...")
            cmd = minecraft_launcher_lib.command.get_minecraft_command(version, self.mc_dir, options)

            self.log("[START] Uruchamianie procesu Minecrafta!")
            subprocess.Popen(cmd)

            self.log("=== GRA URUCHOMIONA PRAWIDŁOWO! UDANEJ ZABAWY ===")
        except Exception as e:
            self.log(f"\n[KRYTYCZNY BŁĄD]: {e}")
            messagebox.showerror("Błąd", f"Nie udało się włączyć gry!\n\nSzczegóły błędu w konsoli programu.")
        finally:
            self.play_btn.config(state="normal", bg="#00E5FF", text="GRAJ TERAZ")

if __name__ == "__main__":
    root = tk.Tk()
    app = PipiLauncherV4(root)
    root.mainloop()
