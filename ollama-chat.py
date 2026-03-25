import tkinter as tk
from tkinter import ttk
import threading
import requests
import json
import os

# ── Config ──────────────────────────────────────────────────────────────────
MODEL = "llama3"
OLLAMA_URL = "https://api.ollama.com/v1/chat/completions"
SYSTEM_PROMPT = "You are a helpful assistant."

BG = "#1e1e2e"
SURFACE = "#2a2a3e"
ACCENT = "#7c6af7"
ACCENT2 = "#a78bfa"
TEXT = "#e2e0ff"
MUTED = "#6e6a9a"
USER_BG = "#3b3560"
BOT_BG = "#252438"
FONT = ("Segoe UI", 11)
FONT_SM = ("Segoe UI", 9)


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cloud Chat")
        self.geometry("720x620")
        self.configure(bg=BG)

        self.history = []
        self.api_key = os.environ.get("OLLAMA_API_KEY", "")

        self._build_ui()
        self._show_welcome()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=SURFACE, pady=10)
        hdr.pack(fill="x")

        tk.Label(hdr, text="✦ Cloud Chat", bg=SURFACE, fg=ACCENT2,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=18)

        tk.Button(hdr, text="Clear", bg=SURFACE, fg=MUTED, bd=0,
                  command=self._clear).pack(side="right", padx=16)

        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical",
                                       command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        self.msg_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas.create_window((0, 0), window=self.msg_frame, anchor="nw")

        self.msg_frame.bind("<Configure>", self._update_scrollregion)

        inp = tk.Frame(self, bg=SURFACE, pady=10)
        inp.pack(fill="x")

        self.input_box = tk.Text(inp, height=3, bg=BG, fg=TEXT,
                                 insertbackground=ACCENT2,
                                 font=FONT, wrap="word")
        self.input_box.pack(side="left", fill="x", expand=True, padx=10)
        self.input_box.bind("<Return>", self._on_enter)

        tk.Button(inp, text="Send", bg=ACCENT, fg="white",
                  command=self._send).pack(side="right", padx=10)

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    def _add_msg(self, role, text):
        frame = tk.Frame(self.msg_frame, bg=BG)
        frame.pack(fill="x", padx=10, pady=4)

        tk.Label(frame, text=("You" if role == "user" else "AI"),
                 fg=ACCENT2 if role == "user" else ACCENT,
                 bg=BG).pack(anchor="e" if role == "user" else "w")

        tk.Label(frame, text=text,
                 bg=USER_BG if role == "user" else BOT_BG,
                 fg=TEXT, wraplength=500, justify="left",
                 padx=10, pady=6).pack(anchor="e" if role == "user" else "w")

        self._update_scrollregion()

    def _show_welcome(self):
        self._add_msg("assistant", "Hey 👋 Ask me anything!")

    def _clear(self):
        for w in self.msg_frame.winfo_children():
            w.destroy()
        self.history.clear()
        self._show_welcome()

    def _on_enter(self, event):
        self._send()
        return "break"

    def _send(self):
        text = self.input_box.get("1.0", "end-1c").strip()
        if not text:
            return

        self.input_box.delete("1.0", "end")
        self._add_msg("user", text)
        self.history.append({"role": "user", "content": text})

        threading.Thread(target=self._call_api, daemon=True).start()

    def _call_api(self):
        if not self.api_key:
            self._add_msg("assistant", "No API key found.")
            return

        try:
            payload = {
                "model": MODEL,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + self.history,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            resp = requests.post(OLLAMA_URL, headers=headers,
                                 data=json.dumps(payload))
            resp.raise_for_status()

            data = resp.json()
            reply = data["choices"][0]["message"]["content"]

            self.history.append({"role": "assistant", "content": reply})
            self._add_msg("assistant", reply)

        except requests.exceptions.HTTPError as e:
            error_text = e.response.text if e.response else str(e)
            self._add_msg("assistant", f"HTTP ERROR:\n{error_text}")

        except Exception as e:
            self._add_msg("assistant", f"ERROR:\n{e}")


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()