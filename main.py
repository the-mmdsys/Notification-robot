# gui.py
import os
import sys
import threading
import subprocess
import time
import shutil
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkfont

try:
    from database import DB_NAME
except Exception:
    DB_NAME = "dorf_bot.db"

#cf
BOT_SCRIPT_NAME = "bot.py"           
BACKUP_FOLDER = "backups_gui"
LOG_FILE = "bot.log"                 
REFRESH_SUBS_INTERVAL_MS = 5000      

os.makedirs(BACKUP_FOLDER, exist_ok=True)

def load_env_file(path=".env"):
    """
    Very small .env parser: KEY=VALUE, supports quoted values.
    Returns dict.
    """
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            # rsq
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            env[key] = val
    return env

class BotControllerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Dorf Bot Controller")
        root.geometry("920x620")
        root.minsize(780, 460)

        self.font = tkfont.Font(family="Segoe UI", size=10)
        self.bold_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        top_frame = tk.Frame(root, bd=0, relief="flat")
        top_frame.pack(fill="x", padx=10, pady=8)

        self.start_btn = tk.Button(top_frame, text="Start Bot", width=12, command=self.start_bot,
                                   bg="#28a745", fg="white", activebackground="#218838", cursor="hand2",
                                   font=self.bold_font)
        self.start_btn.pack(side="left", padx=6)

        self.stop_btn = tk.Button(top_frame, text="Stop Bot", width=12, command=self.stop_bot, state="disabled",
                                  bg="#dc3545", fg="white", activebackground="#c82333", cursor="hand2",
                                  font=self.bold_font)
        self.stop_btn.pack(side="left", padx=6)

        self.backup_btn = tk.Button(top_frame, text="Backup DB", width=12, command=self.manual_backup,
                                    bg="#17a2b8", fg="white", activebackground="#138496", cursor="hand2",
                                    font=self.font)
        self.backup_btn.pack(side="left", padx=6)

        self.openlog_btn = tk.Button(top_frame, text="Open bot.log", width=12, command=self.open_logfile,
                                     bg="#6c757d", fg="white", activebackground="#5a6268", cursor="hand2",
                                     font=self.font)
        self.openlog_btn.pack(side="left", padx=6)

        tk.Frame(top_frame, width=12).pack(side="left")

        tk.Label(top_frame, text="Subscribers:", font=self.font).pack(side="left", padx=(6,2))
        self.subs_label = tk.Label(top_frame, text="0", width=6, font=self.font, bg="#f8f9fa", bd=1, relief="sunken")
        self.subs_label.pack(side="left")

        tk.Button(top_frame, text="Refresh", command=self.refresh_subs_count, width=10,
                  bg="#ffc107", fg="black", activebackground="#e0a800", cursor="hand2", font=self.font).pack(side="left", padx=8)

        status_frame = tk.Frame(root)
        status_frame.pack(fill="x", padx=10)
        self.status_canvas = tk.Canvas(status_frame, width=16, height=16, highlightthickness=0)
        self.status_dot = self.status_canvas.create_oval(2, 2, 14, 14, fill="#6c757d")  
        self.status_canvas.pack(side="left", padx=(0,6))
        self.status_var = tk.StringVar(value="Stopped")
        tk.Label(status_frame, textvariable=self.status_var, font=self.bold_font, fg="#343a40").pack(side="left")

        log_frame = tk.Frame(root, bd=1, relief="sunken")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(8,10))

        self.logbox = ScrolledText(log_frame, state="normal", height=20, wrap="word", font=("Consolas", 10))
        self.logbox.pack(fill="both", expand=True)
        self._init_log_title()

        self.proc = None
        self._reader_thread = None
        self._stop_reader = threading.Event()
        self._last_subs_count = None

        #spr
        self.root.after(1000, self._periodic_refresh_subs)

    def _init_log_title(self):
        self.logbox.delete("1.0", "end")
        title = "Dorf Bot Controller — Logs\n"
        self.logbox.insert("end", title)
        self.logbox.insert("end", "-" * 80 + "\n")
        self.append_log("Ready. Use Start to run the bot.", meta=False)

    def start_bot(self):
        if self.proc and self.proc.poll() is None:
            messagebox.showinfo("Info", "Bot is already running.")
            return

        env = os.environ.copy()
        env_from_file = load_env_file(".env")
        env.update({k: v for k, v in env_from_file.items() if v is not None})
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'

        script_dir = os.path.dirname(os.path.abspath(__file__))
        bot_script = os.path.join(script_dir, BOT_SCRIPT_NAME)
        if not os.path.exists(bot_script):
            messagebox.showerror("Error", f"Bot script not found: {bot_script}")
            return

        python_exe = sys.executable or "python"
        cmd = [python_exe, bot_script]

        try:
            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env,
                cwd=script_dir,
                creationflags=creationflags
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bot: {e}")
            return

        self._stop_reader.clear()
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

        self._set_status_running()
        self.append_log("✅ Bot activated — The bot is now running and listening for messages.", meta=True)
        self.append_log(f"(Process PID: {self.proc.pid})", meta=False)

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def stop_bot(self):
        if not self.proc:
            messagebox.showinfo("Info", "Bot is not running.")
            return
        if self.proc.poll() is not None:
            self.append_log("Process already exited.", meta=False)
            self._on_process_exit()
            return

        self.append_log("⛔ Stopping bot...", meta=True)
        try:
            self.proc.terminate()
            for _ in range(20):
                if self.proc.poll() is not None:
                    break
                time.sleep(0.2)
            else:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        except Exception as e:
            self.append_log(f"Error while stopping: {e}", meta=True)

        self._stop_reader.set()

        self._on_process_exit()
        self.append_log("⛔ Bot stopped — You can start it again anytime.", meta=True)

    def _on_process_exit(self):
        self._set_status_stopped()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.proc = None

    def _reader_loop(self):
        """Read stdout of subprocess and append to log area."""
        try:
            if not self.proc or not self.proc.stdout:
                return
            for raw_line in self.proc.stdout:
                if raw_line is None:
                    break
                line = raw_line.rstrip("\n")
                if line.strip().startswith(">>> Started bot"):
                    continue
                self.append_log(line, prefix="[BOT]", meta=False)
                if self._stop_reader.is_set():
                    break
        except Exception as e:
            self.append_log(f"Reader error: {e}", meta=True)
        finally:
            self.root.after(0, self._on_process_exit)

    def append_log(self, text, prefix=None, meta=True):
        """
        meta: if True, uses prettier message style (bigger emphasis)
        prefix: optional prefix like [BOT]
        """
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if prefix:
            message = f"{ts} {prefix} {text}\n"
        else:
            message = f"{ts} {text}\n"

        def _append():
            if meta:
                self.logbox.insert("end", "\n")
                self.logbox.insert("end", message)
            else:
                self.logbox.insert("end", message)
            self.logbox.see("end")
        try:
            self.logbox.after(0, _append)
        except Exception:
            pass

    def manual_backup(self):
        threading.Thread(target=self._do_backup, daemon=True).start()

    def _do_backup(self):
        src = DB_NAME
        if not os.path.exists(src):
            self.append_log(f"Backup failed: DB not found ({src})", meta=True)
            messagebox.showerror("Error", f"DB file not found: {src}")
            return
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest = os.path.join(BACKUP_FOLDER, f"{os.path.splitext(os.path.basename(src))[0]}_backup_{ts}.db")
        try:
            shutil.copy2(src, dest)
            self.append_log(f"Backup created: {dest}", meta=True)
            messagebox.showinfo("Backup", f"Backup created:\n{dest}")
        except Exception as e:
            self.append_log(f"Backup failed: {e}", meta=True)
            messagebox.showerror("Error", f"Backup failed: {e}")

    def refresh_subs_count(self):
        try:
            if not os.path.exists(DB_NAME):
                self.subs_label.config(text="0")
                return
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM subscribers")
            row = cur.fetchone()
            count = row[0] if row else 0
            conn.close()
            self.subs_label.config(text=str(count))
            self._last_subs_count = count
        except Exception as e:
            self.append_log(f"Failed to read DB: {e}", meta=True)
            self.subs_label.config(text="?")

    def _periodic_refresh_subs(self):
        self.refresh_subs_count()
        self.root.after(REFRESH_SUBS_INTERVAL_MS, self._periodic_refresh_subs)

    # log
    def open_logfile(self):
        logpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILE)
        if not os.path.exists(logpath):
            messagebox.showinfo("Info", f"{LOG_FILE} not found.")
            return
        try:
            if sys.platform == "win32":
                os.startfile(logpath)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", logpath])
            else:
                subprocess.Popen(["xdg-open", logpath])
        except Exception as e:
            messagebox.showerror("Error", f"Can't open log file: {e}")

    def _set_status_running(self):
        self.status_canvas.itemconfig(self.status_dot, fill="#28a745")  
        self.status_var.set("Running")

    def _set_status_stopped(self):
        self.status_canvas.itemconfig(self.status_dot, fill="#6c757d")  
        self.status_var.set("Stopped")

    def on_close(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("Exit", "Bot is still running. Stop it and exit?"):
                try:
                    self.proc.terminate()
                except Exception:
                    pass
                time.sleep(0.3)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BotControllerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
