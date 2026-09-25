import tkinter as tk
from tkinter import messagebox
import threading
import time
from datetime import datetime

try:
    import requests
except ImportError:
    raise SystemExit("Install requests first: py -m pip install requests")

BG = "#070914"
PANEL = "#0d1020"
PANEL2 = "#11162a"
CYAN = "#00f6ff"
MAGENTA = "#ff2bd6"
PURPLE = "#8b5cff"
GREEN = "#43ff8b"
YELLOW = "#ffe66d"
WHITE = "#e8f7ff"
MUTED = "#71809c"
GRID = "#18213a"
FONT = "Consolas"


class CyberButton(tk.Button):
    def __init__(self, master, **kw):
        kw.update({
            "bg": kw.get("bg", PANEL2),
            "fg": kw.get("fg", CYAN),
            "activebackground": "#1b2440",
            "activeforeground": WHITE,
            "relief": "flat",
            "bd": 0,
            "font": (FONT, 10, "bold"),
            "cursor": "hand2"
        })
        super().__init__(master, **kw)


class Radar(tk.Canvas):
    def __init__(self, master):
        super().__init__(
            master, bg="#080b16", highlightthickness=1,
            highlightbackground=PURPLE
        )
        self.lat = None
        self.lon = None
        self.bind("<Configure>", lambda e: self.draw())

    def set_location(self, lat, lon):
        self.lat, self.lon = lat, lon
        self.draw()

    def draw(self):
        self.delete("all")
        w = max(self.winfo_width(), 500)
        h = max(self.winfo_height(), 300)

        for x in range(0, w, 32):
            self.create_line(x, 0, x, h, fill=GRID)
        for y in range(0, h, 32):
            self.create_line(0, y, w, y, fill=GRID)

        self.create_text(
            20, 20, anchor="nw",
            text="LIVE TELEMETRY // GPS VISUALIZER",
            fill=CYAN, font=(FONT, 10, "bold")
        )

        if self.lat is None:
            self.create_text(
                w/2, h/2,
                text="AWAITING GPS TELEMETRY",
                fill=MUTED, font=(FONT, 16, "bold")
            )
            return

        x = ((self.lon + 180) / 360) * w
        y = ((90 - self.lat) / 180) * h
        x = max(30, min(w-30, x))
        y = max(60, min(h-30, y))

        for r in (55, 35, 18):
            self.create_oval(
                x-r, y-r, x+r, y+r,
                outline=CYAN, width=1
            )

        self.create_line(x-70, y, x+70, y, fill=MAGENTA)
        self.create_line(x, y-70, x, y+70, fill=MAGENTA)
        self.create_oval(
            x-8, y-8, x+8, y+8,
            fill=MAGENTA, outline=CYAN, width=2
        )
        self.create_text(
            x+14, y-15, anchor="sw",
            text=f"{self.lat:.6f}, {self.lon:.6f}",
            fill=WHITE, font=(FONT, 9, "bold")
        )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PHONETRACKER // CYBERPUNK CONTROL")
        self.geometry("1150x740")
        self.minsize(950, 620)
        self.configure(bg=BG)

        self.api = tk.StringVar(value="http://localhost:5080")
        self.code = tk.StringVar()
        self.status = tk.StringVar(value="OFFLINE")
        self.device = tk.StringVar(value="NO DEVICE")
        self.coords = tk.StringVar(value="--")
        self.last = tk.StringVar(value="--")
        self.accuracy = tk.StringVar(value="--")
        self.battery = tk.StringVar(value="--")

        self.token = None
        self.running = False
        self.http = requests.Session()

        self.build()

    def build(self):
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=18, pady=16)

        tk.Label(
            head, text="◈ PHONE", bg=BG, fg=CYAN,
            font=(FONT, 25, "bold")
        ).pack(side="left")

        tk.Label(
            head, text="TRACKER", bg=BG, fg=MAGENTA,
            font=(FONT, 25, "bold")
        ).pack(side="left")

        tk.Label(
            head,
            text="  //  CYBERPUNK COMMAND CONSOLE",
            bg=BG, fg=MUTED, font=(FONT, 10, "bold")
        ).pack(side="left", pady=10)

        self.led = tk.Label(
            head, text="● SYSTEM READY",
            bg=BG, fg=GREEN, font=(FONT, 10, "bold")
        )
        self.led.pack(side="right")

        conn = tk.Frame(
            self, bg=PANEL,
            highlightbackground=PURPLE,
            highlightthickness=1
        )
        conn.pack(fill="x", padx=18, pady=5)

        tk.Label(
            conn, text="API ENDPOINT",
            bg=PANEL, fg=MUTED, font=(FONT, 9, "bold")
        ).grid(row=0, column=0, padx=12, pady=14)

        tk.Entry(
            conn, textvariable=self.api,
            bg="#080b16", fg=CYAN,
            insertbackground=CYAN,
            relief="flat", font=(FONT, 10), width=34
        ).grid(row=0, column=1)

        CyberButton(
            conn, text="GENERATE PAIR CODE",
            command=self.create_pairing
        ).grid(row=0, column=2, padx=12)

        tk.Label(
            conn, text="PAIR CODE",
            bg=PANEL, fg=MUTED, font=(FONT, 9, "bold")
        ).grid(row=0, column=3, padx=5)

        tk.Label(
            conn, textvariable=self.code,
            bg="#080b16", fg=YELLOW,
            font=(FONT, 18, "bold"), width=8
        ).grid(row=0, column=4, padx=8)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=12)

        left = tk.Frame(body, bg=BG, width=280)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        self.card(left, "LINK STATUS", self.status, CYAN)
        self.card(left, "DEVICE", self.device, MAGENTA)
        self.card(left, "COORDINATES", self.coords, CYAN)
        self.card(left, "LAST TELEMETRY", self.last, GREEN)
        self.card(left, "GPS ACCURACY", self.accuracy, YELLOW)
        self.card(left, "BATTERY", self.battery, MAGENTA)

        CyberButton(
            left, text="STOP POLLING",
            command=self.stop
        ).pack(fill="x", pady=12, ipady=8)

        CyberButton(
            left, text="CLEAR SESSION",
            command=self.clear
        ).pack(fill="x", ipady=8)

        self.radar = Radar(body)
        self.radar.pack(side="left", fill="both", expand=True)

        tk.Label(
            self,
            text="AUTHORIZED DEVICES ONLY // LOCATION IS PROVIDED BY THE ANDROID DEVICE",
            bg=BG, fg=MUTED, font=(FONT, 8, "bold")
        ).pack(pady=8)

    def card(self, parent, title, variable, accent):
        frame = tk.Frame(
            parent, bg=PANEL,
            highlightbackground=accent,
            highlightthickness=1
        )
        frame.pack(fill="x", pady=5)

        tk.Label(
            frame, text=title,
            bg=PANEL, fg=MUTED,
            font=(FONT, 8, "bold")
        ).pack(anchor="w", padx=12, pady=(8, 2))

        tk.Label(
            frame, textvariable=variable,
            bg=PANEL, fg=accent,
            font=(FONT, 10, "bold"),
            wraplength=245, justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 9))

    def create_pairing(self):
        def worker():
            try:
                r = self.http.post(
                    self.api.get().rstrip("/") + "/api/pair/create",
                    timeout=8
                )
                r.raise_for_status()
                data = r.json()

                self.token = data["desktopToken"]
                self.after(0, lambda: self.code.set(data["code"]))
                self.after(0, lambda: self.status.set("WAITING FOR ANDROID"))
                self.after(0, self.start)
            except Exception as e:
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Connection Error",
                        str(e)
                    )
                )

        threading.Thread(target=worker, daemon=True).start()

    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self.poll_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.status.set("POLLING STOPPED")

    def poll_loop(self):
        while self.running and self.token:
            try:
                headers = {"Authorization": "Bearer " + self.token}
                base = self.api.get().rstrip("/")

                pair = self.http.get(
                    base + "/api/pair/status",
                    headers=headers, timeout=6
                )

                if pair.ok:
                    data = pair.json()

                    if data.get("paired"):
                        self.after(
                            0,
                            lambda: self.status.set("LINKED // ONLINE")
                        )
                        self.after(
                            0,
                            lambda: self.device.set(
                                data.get("deviceName", "ANDROID DEVICE")
                            )
                        )

                        loc = self.http.get(
                            base + "/api/location",
                            headers=headers, timeout=6
                        )

                        if loc.ok:
                            self.update_location(loc.json())
                    else:
                        self.after(
                            0,
                            lambda: self.status.set("WAITING FOR ANDROID")
                        )

            except Exception:
                self.after(
                    0,
                    lambda: self.status.set("API CONNECTION ERROR")
                )

            time.sleep(3)

    def update_location(self, data):
        lat = data.get("latitude")
        lon = data.get("longitude")
        acc = data.get("accuracyMeters")
        batt = data.get("batteryPercent")
        timestamp = data.get("timestamp")

        if lat is not None and lon is not None:
            self.after(
                0,
                lambda: self.coords.set(
                    f"{lat:.6f}, {lon:.6f}"
                )
            )
            self.after(
                0,
                lambda: self.radar.set_location(lat, lon)
            )

        self.after(
            0,
            lambda: self.accuracy.set(
                f"{acc:.1f} m" if acc is not None else "--"
            )
        )

        self.after(
            0,
            lambda: self.battery.set(
                f"{batt}%" if batt is not None else "--"
            )
        )

        if timestamp:
            try:
                dt = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                ).astimezone()
                value = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                value = timestamp
        else:
            value = "--"

        self.after(0, lambda: self.last.set(value))

    def clear(self):
        self.running = False
        self.token = None
        self.code.set("")
        self.status.set("OFFLINE")
        self.device.set("NO DEVICE")
        self.coords.set("--")
        self.last.set("--")
        self.accuracy.set("--")
        self.battery.set("--")
        self.radar.lat = None
        self.radar.lon = None
        self.radar.draw()


if __name__ == "__main__":
    App().mainloop()
