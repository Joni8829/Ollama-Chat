import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import requests
import json
import os

# ── Config ──────────────────────────────────────────────────────────────────
MODEL        = "gpt-oss:20b-cloud"
OLLAMA_URL   = "https://api.ollama.com/v1/chat/completions"
SYSTEM_PROMPT = "You are a helpful assistant."

BG       = "#1e1e2e"
SURFACE  = "#2a2a3e"
ACCENT   = "#7c6af7"
ACCENT2  = "#a78bfa"
TEXT     = "#e2e0ff"
MUTED    = "#6e6a9a"
USER_BG  = "#3b3560"
BOT_BG   = "#252438"
FONT     = ("Segoe UI", 11)
FONT_SM  = ("Segoe UI", 9)


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPT-OSS Chat")
        self.geometry("720x620")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(480, 400)

        self.history: list[dict] = []
        self.api_key = os.environ.get("OLLAMA_API_KEY", "")

        self._build_ui()
        self._show_welcome()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✦  GPT-OSS Chat", bg=SURFACE, fg=ACCENT2,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=18)
        tk.Button(hdr, text="Clear", bg=SURFACE, fg=MUTED, bd=0,
                  activebackground=SURFACE, activeforeground=TEXT, cursor="hand2",
                  font=FONT_SM, command=self._clear).pack(side="right", padx=16)

        # Message canvas
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical",
                                       command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        self.msg_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.msg_frame, anchor="nw")

        self.msg_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self.canvas.bind_all("<Button-5>",   self._on_mousewheel)

        # Input area
        inp = tk.Frame(self, bg=SURFACE, pady=10)
        inp.pack(fill="x", side="bottom")

        self.input_box = tk.Text(inp, height=3, bg=BG, fg=TEXT,
                                 insertbackground=ACCENT2, relief="flat",
                                 font=FONT, padx=12, pady=8, wrap="word",
                                 highlightthickness=1, highlightbackground=ACCENT)
        self.input_box.pack(side="left", fill="x", expand=True, padx=(14, 8))
        self.input_box.bind("<Return>",       self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)

        self.send_btn = tk.Button(inp, text="Send", bg=ACCENT, fg="white",
                                  activebackground=ACCENT2, activeforeground="white",
                                  relief="flat", font=("Segoe UI", 11, "bold"),
                                  padx=18, pady=6, cursor="hand2",
                                  command=self._send)
        self.send_btn.pack(side="right", padx=(0, 14))

    # ── Scroll helpers ────────────────────────────────────────────────────────
    def _on_frame_configure(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_bottom(self):
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # ── Messages ──────────────────────────────────────────────────────────────
    def _show_welcome(self):
        self._add_bubble("assistant",
            "Hey 👋  I'm GPT-OSS, an open-weight model by OpenAI running via Ollama. Ask me anything!")

    def _clear(self):
        for w in self.msg_frame.winfo_children():
            w.destroy()
        self.history.clear()
        self._show_welcome()

    def _add_bubble(self, role: str, text: str) -> tk.Label:
        is_user = role == "user"
        outer = tk.Frame(self.msg_frame, bg=BG)
        outer.pack(fill="x", padx=14, pady=4)

        label_text  = "You" if is_user else "GPT-OSS"
        label_color = ACCENT2 if is_user else ACCENT

        tk.Label(outer, text=label_text, bg=BG, fg=label_color,
                 font=("Segoe UI", 9, "bold")).pack(anchor="e" if is_user else "w")

        bubble = tk.Label(outer, text=text, bg=USER_BG if is_user else BOT_BG,
                          fg=TEXT, font=FONT, wraplength=480,
                          justify="left", padx=14, pady=10, relief="flat",
                          anchor="w")
        bubble.pack(anchor="e" if is_user else "w")
        self._scroll_bottom()
        return bubble

    def _add_thinking(self) -> tk.Frame:
        outer = tk.Frame(self.msg_frame, bg=BG)
        outer.pack(fill="x", padx=14, pady=4)
        tk.Label(outer, text="GPT-OSS", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(outer, text="● thinking…", bg=BOT_BG, fg=MUTED,
                 font=FONT, padx=14, pady=10).pack(anchor="w")
        self._scroll_bottom()
        return outer

    # ── Send / API ────────────────────────────────────────────────────────────
    def _on_enter(self, event):
        if not event.state & 0x1:
            self._send()
            return "break"

    def _send(self):
        text = self.input_box.get("1.0", "end-1c").strip()
        if not text:
            return
        self.input_box.delete("1.0", "end")
        self._add_bubble("user", text)
        self.history.append({"role": "user", "content": text})
        self.send_btn.configure(state="disabled")
        thinking = self._add_thinking()
        threading.Thread(target=self._call_api, args=(thinking,), daemon=True).start()

    def _call_api(self, thinking_frame: tk.Frame):
        if not self.api_key:
            self.after(0, lambda: self._finish(thinking_frame,
                "⚠️  No API key found. Set OLLAMA_API_KEY and restart."))
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
                                 data=json.dumps(payload), timeout=60)
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            self.after(0, lambda: self._finish(thinking_frame, reply))
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                msg = "⚠️  Authentication failed — check your OLLAMA_API_KEY."
            else:
                msg = f"⚠️  HTTP error: {e}"
            self.after(0, lambda: self._finish(thinking_frame, msg))
        except Exception as e:
            self.after(0, lambda: self._finish(thinking_frame, f"⚠️  Error: {e}"))

    def _finish(self, thinking_frame: tk.Frame, reply: str):
        thinking_frame.destroy()
        self._add_bubble("assistant", reply)
        self.send_btn.configure(state="normal")
        self.input_box.focus_set()


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()