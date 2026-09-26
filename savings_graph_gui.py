# savings_graph_gui.py
"""
SavingsGraphWindow

Shows monthly savings in a matplotlib graph embedded in Tkinter/ttkbootstrap.

Features:
- Dropdown for interval (3m, 6m, 1y, 2y, 5y, 10y — limited to available data).
- Graph spans 1st and 4th quadrants (positive/negative savings).
- Axis lines always drawn in the negative of background color (white on dark, black on light).
- Average line for the selected interval.
- Fully responsive: graph scales with window, labels never clip.
- Warning suppression for matplotlib's 'tight_layout changed' messages.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import statistics
import warnings

# Suppress harmless matplotlib tight_layout warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


class SavingsGraphWindow:
    INTERVALS_MONTHS = [
        (3, "3 months"),
        (6, "6 months"),
        (12, "1 year"),
        (24, "2 years"),
        (60, "5 years"),
        (120, "10 years"),
    ]

    def __init__(self, parent, user_id, db_conn=None, theme_bg="#222222", theme_fg=None):
        self.parent = parent
        self.user_id = user_id
        self.db_conn = db_conn
        self.theme_bg = theme_bg or "#222222"
        self.theme_fg = theme_fg or ("#ffffff" if self._is_dark(self.theme_bg) else "#000000")

        # Axis always negative of background
        self.axis_color = "#ffffff" if self._is_dark(self.theme_bg) else "#000000"

        self.all_dates = []
        self.all_values = []

        # UI
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.controls_frame = ttk.Frame(self.frame)
        self.controls_frame.pack(side="top", fill="x", padx=8, pady=(8, 4))

        ttk.Label(self.controls_frame, text="Interval:").pack(side="left", padx=(4, 6))
        self.interval_var = tk.StringVar()
        self.interval_box = ttk.Combobox(
            self.controls_frame, textvariable=self.interval_var, state="readonly", width=16
        )
        self.interval_box.pack(side="left")
        self.interval_box.bind("<<ComboboxSelected>>", lambda e: self._on_interval_changed())

        self.info_label = ttk.Label(self.controls_frame, text="", font=("Helvetica", 9, "italic"))
        self.info_label.pack(side="left", padx=(8, 4))

        self.canvas_container = ttk.Frame(self.frame)
        self.canvas_container.pack(fill="both", expand=True, padx=6, pady=6)

        self.fig = None
        self.ax = None
        self.canvas = None
        self.canvas_widget = None
        self._interval_map = {}

        self._load_monthly_savings()

        # Fix clipping: redraw after widget is visible
        self.frame.after(120, self._ensure_initial_draw)

        self.frame.bind("<Configure>", self._on_resize)

    # ---------------- Data ----------------
    def _get_connection(self):
        try:
            if callable(self.db_conn):
                return self.db_conn()
            if self.db_conn and hasattr(self.db_conn, "cursor"):
                return self.db_conn
        except Exception:
            return None
        return None

    def _load_monthly_savings(self):
        rows = []
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT month, savings FROM monthly_savings WHERE user_id = %s ORDER BY month ASC",
                    (self.user_id,),
                )
                rows = cur.fetchall()
                cur.close()
        except Exception as e:
            self.info_label.config(text=f"DB error: {e}")

        self.all_dates, self.all_values = [], []
        for d, val in rows:
            if isinstance(d, str):
                d = datetime.fromisoformat(d).date()
            self.all_dates.append(d)
            self.all_values.append(float(val))

        available = len(self.all_dates)
        self.info_label.config(text=f"{available} month(s) available")

        choices = []
        self._interval_map = {}
        for months, label in self.INTERVALS_MONTHS:
            if months <= available:
                choices.append(label)
                self._interval_map[label] = months
        if not choices and available:
            label = f"All ({available} months)"
            choices = [label]
            self._interval_map[label] = available

        self.interval_box["values"] = choices
        if choices:
            self.interval_var.set(choices[-1])
            self._plot_interval(self._interval_map[choices[-1]])
        else:
            self._show_no_data_message()

    # ---------------- Plot ----------------
    def _create_figure_if_needed(self):
        if self.fig:
            return
        w, h, dpi = 700, 400, 100
        self.fig = Figure(figsize=(w / dpi, h / dpi), dpi=dpi, facecolor=self.theme_bg)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.12, right=0.96, top=0.94, bottom=0.20)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_container)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def _show_no_data_message(self):
        for w in self.canvas_container.winfo_children():
            w.destroy()
        ttk.Label(
            self.canvas_container,
            text="No monthly savings data available for this user.",
            font=("Helvetica", 12, "bold"),
        ).pack(expand=True)

    def _plot_interval(self, months):
        if not self.all_values:
            self._show_no_data_message()
            return

        n = months
        dates = self.all_dates[-n:]
        values = self.all_values[-n:]
        x = list(range(1, n + 1))
        avg = statistics.mean(values)

        self._create_figure_if_needed()
        self.ax.clear()
        self.fig.patch.set_facecolor(self.theme_bg)
        self.ax.set_facecolor(self.theme_bg)

        main_line, avg_line = ("#00ffd1", "#ffcc66") if self._is_dark(self.theme_bg) else ("#0066cc", "#cc5500")
        grid_color = self._blend_color(self.axis_color, self.theme_bg, 0.15)

        self.ax.plot(x, values, marker="o", linewidth=2.2, color=main_line, label="Savings")
        self.ax.hlines(avg, 0.8, n + 0.2, colors=avg_line, linestyles="--", linewidth=2.0, label=f"Avg: ₹{avg:,.2f}")

        self.ax.axhline(0, color=self.axis_color, linewidth=1.2)
        self.ax.axvline(0, color=self.axis_color, linewidth=1.0)

        self.ax.set_xticks(x)
        self.ax.set_xticklabels([d.strftime("%b %Y") for d in dates], rotation=45, ha="right")

        max_val = max(abs(min(values)), abs(max(values)), abs(avg), 1)
        self.ax.set_ylim(-1.15 * max_val, 1.15 * max_val)
        self.ax.set_xlim(0.6, n + 0.4)

        self.ax.grid(True, linestyle=":", linewidth=0.6, color=grid_color)
        for spine in ("top", "right"):
            self.ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            self.ax.spines[spine].set_color(self.axis_color)

        self.ax.tick_params(colors=self.axis_color)
        for lbl in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            lbl.set_color(self.axis_color)

        self.ax.set_title("Monthly Savings", color=self.axis_color, fontsize=12)
        leg = self.ax.legend(facecolor=self.theme_bg)
        for t in leg.get_texts():
            t.set_color(self.axis_color)

        self.fig.tight_layout(rect=[0.08, 0.08, 0.96, 0.95])
        self.canvas.draw_idle()

    # ---------------- Events ----------------
    def _on_interval_changed(self):
        sel = self.interval_var.get()
        months = self._interval_map.get(sel, len(self.all_dates))
        self._plot_interval(months)

    def _on_resize(self, event=None):
        if not self.fig:
            return
        w, h = self.canvas_container.winfo_width(), self.canvas_container.winfo_height()
        dpi = self.fig.get_dpi()
        self.fig.set_size_inches(max(1, w / dpi), max(1, h / dpi))
        self.canvas.draw_idle()

    def _ensure_initial_draw(self):
        sel = self.interval_var.get()
        months = self._interval_map.get(sel, len(self.all_dates))
        if months:
            self._plot_interval(months)

    # ---------------- Utils ----------------
    @staticmethod
    def _is_dark(hexc):
        h = hexc.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b < 130

    @staticmethod
    def _blend_color(fg, bg, alpha=0.5):
        fr, fg_, fb = int(fg[1:3], 16), int(fg[3:5], 16), int(fg[5:7], 16)
        br, bg_, bb = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
        r = int((1 - alpha) * br + alpha * fr)
        g = int((1 - alpha) * bg_ + alpha * fg_)
        b = int((1 - alpha) * bb + alpha * fb)
        return f"#{r:02x}{g:02x}{b:02x}"
