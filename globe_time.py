import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pytz
from zoneinfo import available_timezones

# --- City to timezone mapping ---
CITY_TIMEZONES = {
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "dubai": "Asia/Dubai",
    "mumbai": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "singapore": "Asia/Singapore",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "toronto": "America/Toronto",
    "sao paulo": "America/Sao_Paulo",
    "moscow": "Europe/Moscow",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "seoul": "Asia/Seoul",
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "mexico city": "America/Mexico_City",
    "amsterdam": "Europe/Amsterdam",
    "rome": "Europe/Rome",
    "madrid": "Europe/Madrid",
    "istanbul": "Europe/Istanbul",
    "bangkok": "Asia/Bangkok",
    "jakarta": "Asia/Jakarta",
    "karachi": "Asia/Karachi",
    "lagos": "Africa/Lagos",
    "nairobi": "Africa/Nairobi",
    "riyadh": "Asia/Riyadh",
    "hong kong": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei",
    "kuala lumpur": "Asia/Kuala_Lumpur",
    "lima": "America/Lima",
    "bogota": "America/Bogota",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "santiago": "America/Santiago",
    "vancouver": "America/Vancouver",
    "auckland": "Pacific/Auckland",
    "honolulu": "Pacific/Honolulu",
    "denver": "America/Denver",
    "phoenix": "America/Phoenix",
    "seattle": "America/Los_Angeles",
    "miami": "America/New_York",
    "boston": "America/New_York",
    "atlanta": "America/New_York",
    "dallas": "America/Chicago",
    "houston": "America/Chicago",
    "chennai": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "hyderabad": "Asia/Kolkata",
    "lahore": "Asia/Karachi",
    "dhaka": "Asia/Dhaka",
    "kathmandu": "Asia/Kathmandu",
    "colombo": "Asia/Colombo",
    "tehran": "Asia/Tehran",
    "baghdad": "Asia/Baghdad",
    "tel aviv": "Asia/Jerusalem",
    "athens": "Europe/Athens",
    "warsaw": "Europe/Warsaw",
    "budapest": "Europe/Budapest",
    "prague": "Europe/Prague",
    "vienna": "Europe/Vienna",
    "zurich": "Europe/Zurich",
    "lisbon": "Europe/Lisbon",
    "brussels": "Europe/Brussels",
    "stockholm": "Europe/Stockholm",
    "oslo": "Europe/Oslo",
    "copenhagen": "Europe/Copenhagen",
    "helsinki": "Europe/Helsinki",
}

class WorldClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 World Clock")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        self.root.minsize(500, 400)

        self.clocks = []  # list of (city_name, timezone_str, frame, time_label)

        self.build_ui()
        self.update_clocks()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a2e")
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header,
            text="🌍 World Clock",
            font=("Helvetica", 22, "bold"),
            bg="#1a1a2e",
            fg="#e0e0e0"
        ).pack(side="left")

        # Search bar area
        search_frame = tk.Frame(self.root, bg="#1a1a2e")
        search_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Helvetica", 13),
            bg="#16213e",
            fg="#e0e0e0",
            insertbackground="#e0e0e0",
            relief="flat",
            bd=8,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.search_entry.insert(0, "Search city (e.g. Tokyo, London)...")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_placeholder)
        self.search_entry.bind("<Return>", lambda e: self.add_clock())

        add_btn = tk.Button(
            search_frame,
            text="Add",
            font=("Helvetica", 12, "bold"),
            bg="#e94560",
            fg="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.add_clock,
        )
        add_btn.pack(side="left", padx=(10, 0))

        # Scrollable clock list
        container = tk.Frame(self.root, bg="#1a1a2e")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        canvas = tk.Canvas(container, bg="#1a1a2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.clock_frame = tk.Frame(canvas, bg="#1a1a2e")

        self.clock_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.clock_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add default cities
        for city in ["New York", "London", "Tokyo", "Mumbai"]:
            self._add_clock_card(city, CITY_TIMEZONES[city.lower()])

    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search city (e.g. Tokyo, London)...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="#e0e0e0")

    def restore_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search city (e.g. Tokyo, London)...")
            self.search_entry.config(fg="#555577")

    def add_clock(self):
        query = self.search_var.get().strip().lower()
        if query == "search city (e.g. tokyo, london)..." or not query:
            return

        if query in CITY_TIMEZONES:
            tz_str = CITY_TIMEZONES[query]
            city_display = query.title()
            # Don't add duplicates
            for city, _, _, _ in self.clocks:
                if city.lower() == city_display.lower():
                    messagebox.showinfo("Already added", f"{city_display} is already on your clock!")
                    return
            self._add_clock_card(city_display, tz_str)
            self.search_entry.delete(0, tk.END)
        else:
            messagebox.showwarning(
                "City not found",
                f'"{query.title()}" not found.\n\nTry cities like: New York, London, Tokyo, Paris, Dubai, Sydney...'
            )

    def _add_clock_card(self, city_name, tz_str):
        card = tk.Frame(
            self.clock_frame,
            bg="#16213e",
            bd=0,
            relief="flat",
        )
        card.pack(fill="x", pady=6, ipady=12, ipadx=15)

        left = tk.Frame(card, bg="#16213e")
        left.pack(side="left", fill="both", expand=True, padx=15)

        city_label = tk.Label(
            left,
            text=city_name,
            font=("Helvetica", 14, "bold"),
            bg="#16213e",
            fg="#e0e0e0",
            anchor="w"
        )
        city_label.pack(anchor="w")

        tz_label = tk.Label(
            left,
            text=tz_str,
            font=("Helvetica", 9),
            bg="#16213e",
            fg="#888899",
            anchor="w"
        )
        tz_label.pack(anchor="w")

        time_label = tk.Label(
            card,
            text="--:--:--",
            font=("Courier", 26, "bold"),
            bg="#16213e",
            fg="#e94560",
            anchor="e"
        )
        time_label.pack(side="right", padx=15)

        remove_btn = tk.Button(
            card,
            text="✕",
            font=("Helvetica", 10),
            bg="#16213e",
            fg="#555577",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda c=card, cn=city_name: self.remove_clock(c, cn)
        )
        remove_btn.pack(side="right")

        self.clocks.append((city_name, tz_str, card, time_label))

    def remove_clock(self, card, city_name):
        self.clocks = [(c, tz, f, lbl) for c, tz, f, lbl in self.clocks if c != city_name]
        card.destroy()

    def update_clocks(self):
        for city, tz_str, frame, time_label in self.clocks:
            try:
                tz = pytz.timezone(tz_str)
                now = datetime.now(tz)
                time_label.config(text=now.strftime("%H:%M:%S"))
            except Exception:
                time_label.config(text="Error")
        self.root.after(1000, self.update_clocks)


if __name__ == "__main__":
    root = tk.Tk()
    app = WorldClockApp(root)
    root.mainloop()
