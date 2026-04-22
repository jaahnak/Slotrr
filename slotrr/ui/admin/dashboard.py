import tkinter as tk
from tkinter import ttk
from slotrr.db import db
from slotrr.ui.theme import theme
from typing import List, Dict

# ── Accent palette for stat cards ────────────────────────────────
CARD_COLORS = {
    'rooms':    {'accent': '#3B82F6', 'bg': '#172554', 'border': '#1E3A8A'},  # blue
    'bookings': {'accent': '#F59E0B', 'bg': '#1C1408', 'border': '#78350F'},  # amber
    'teachers': {'accent': '#8B5CF6', 'bg': '#1E1338', 'border': '#4C1D95'},  # violet
    'students': {'accent': '#10B981', 'bg': '#082F23', 'border': '#065F46'},  # green
}

BADGE_COLORS = [
    '#10B981', '#F59E0B', '#3B82F6', '#EC4899',
    '#8B5CF6', '#14B8A6', '#F97316', '#6366F1',
]

PAGE_BG   = '#0F1117'
CARD_BG   = '#151C2C'
TABLE_BG  = '#151C2C'
HEADER_FG = '#64748B'
TEXT_FG   = '#E2E8F0'
SUB_FG    = '#94A3B8'
ROW_ALT   = '#1A2236'
BORDER    = '#1E293B'


class AdminDashboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=PAGE_BG)
        self._build_ui()

    # ── Main layout ──────────────────────────────────────────────

    def _build_ui(self):
        # Scrollable wrapper
        outer = tk.Frame(self, bg=PAGE_BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Title
        tk.Label(outer, text="Admin Dashboard",
                 font=theme.get_font(20, True),
                 fg=TEXT_FG, bg=PAGE_BG).pack(anchor="w", pady=(0, 20))

        # ── Stat cards row ───────────────────────────────────────
        stats = db.get_stats()
        cards_frame = tk.Frame(outer, bg=PAGE_BG)
        cards_frame.pack(fill=tk.X, pady=(0, 28))

        card_data = [
            (str(stats['total_rooms']),           "Total Rooms",           'rooms'),
            (str(stats['active_bookings_today']), "Active Bookings Today", 'bookings'),
            (str(stats['total_teachers']),        "Total Teachers",        'teachers'),
            (str(stats['total_students']),        "Total Students",        'students'),
        ]

        for i, (value, label, key) in enumerate(card_data):
            cards_frame.grid_columnconfigure(i, weight=1)
            self._stat_card(cards_frame, value, label, CARD_COLORS[key], i)

        # ── Recent Bookings ──────────────────────────────────────
        tk.Label(outer, text="Recent Bookings",
                 font=theme.get_font(15, True),
                 fg=TEXT_FG, bg=PAGE_BG).pack(anchor="w", pady=(0, 12))

        self._bookings_table(outer)

    # ── Stat card widget ─────────────────────────────────────────

    def _stat_card(self, parent, value, label, colors, col):
        card = tk.Frame(parent, bg=colors['bg'],
                        highlightbackground=colors['border'],
                        highlightthickness=1, padx=24, pady=18)
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0),
                  sticky="nsew")

        tk.Label(card, text=value,
                 font=theme.get_font(28, True),
                 fg=colors['accent'], bg=colors['bg']).pack(anchor="w")

        tk.Label(card, text=label,
                 font=theme.get_font(10),
                 fg=SUB_FG, bg=colors['bg']).pack(anchor="w", pady=(2, 0))

    # ── Bookings table ───────────────────────────────────────────

    def _bookings_table(self, parent):
        table_frame = tk.Frame(parent, bg=TABLE_BG,
                               highlightbackground=BORDER,
                               highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Column config: (text, width_px)
        columns = [
            ("TEACHER",  250),
            ("ROOM",     160),
            ("SUBJECT",  180),
            ("DATE",     140),
            ("TIME",     160),
        ]

        # Header row
        header = tk.Frame(table_frame, bg=TABLE_BG, pady=10)
        header.pack(fill=tk.X, padx=20)
        
        for text, width in columns:
            col_frame = tk.Frame(header, bg=TABLE_BG, width=width, height=20)
            col_frame.pack_propagate(False)
            col_frame.pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(col_frame, text=text,
                     font=theme.get_font(9, True),
                     fg=HEADER_FG, bg=TABLE_BG,
                     anchor="w").pack(side=tk.LEFT)

        # Separator
        tk.Frame(table_frame, bg=BORDER, height=1).pack(fill=tk.X, padx=16)

        # Data rows
        bookings = db.get_recent_bookings(10)

        if not bookings:
            tk.Label(table_frame, text="No bookings yet",
                     font=theme.get_font(11),
                     fg=SUB_FG, bg=TABLE_BG).pack(pady=30)
            return

        for idx, booking in enumerate(bookings):
            row_bg = ROW_ALT if idx % 2 == 0 else TABLE_BG
            row = tk.Frame(table_frame, bg=row_bg, pady=10)
            row.pack(fill=tk.X, padx=20)

            teacher_name = booking.get('users', {}).get('full_name', 'Unknown')
            room_name    = booking.get('classrooms', {}).get('name', 'Unknown')
            subject      = booking.get('subject_name', '')
            date_str     = booking.get('date', '')
            start        = booking.get('start_time', '')[:5]   # HH:MM
            end          = booking.get('end_time', '')[:5]

            # ── Col 0: Teacher with avatar ───────────────────────
            teacher_col = tk.Frame(row, bg=row_bg, width=columns[0][1], height=32)
            teacher_col.pack_propagate(False)
            teacher_col.pack(side=tk.LEFT, padx=(0, 10))

            # Circular initials avatar
            initials = "".join(w[0].upper() for w in teacher_name.split()[:2])
            avatar_color = BADGE_COLORS[hash(teacher_name) % len(BADGE_COLORS)]
            avatar = tk.Canvas(teacher_col, width=32, height=32,
                               bg=row_bg, highlightthickness=0)
            avatar.pack(side=tk.LEFT, padx=(0, 10))
            avatar.create_oval(2, 2, 30, 30, fill=avatar_color, outline="")
            avatar.create_text(16, 16, text=initials,
                               font=theme.get_font(9, True), fill="#FFFFFF")

            tk.Label(teacher_col, text=teacher_name,
                     font=theme.get_font(11),
                     fg=TEXT_FG, bg=row_bg,
                     anchor="w").pack(side=tk.LEFT)

            # ── Col 1: Room as colored badge ─────────────────────
            room_col = tk.Frame(row, bg=row_bg, width=columns[1][1], height=32)
            room_col.pack_propagate(False)
            room_col.pack(side=tk.LEFT, padx=(0, 10))

            badge_color = BADGE_COLORS[hash(room_name) % len(BADGE_COLORS)]
            badge = tk.Label(room_col, text=f"  {room_name}  ",
                             font=theme.get_font(9, True),
                             fg="#FFFFFF", bg=badge_color,
                             padx=8, pady=2)
            badge.pack(anchor="w", pady=4)

            # ── Col 2: Subject ───────────────────────────────────
            subj_col = tk.Frame(row, bg=row_bg, width=columns[2][1], height=32)
            subj_col.pack_propagate(False)
            subj_col.pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(subj_col, text=subject,
                     font=theme.get_font(11),
                     fg=TEXT_FG, bg=row_bg, anchor="w"
                     ).pack(side=tk.LEFT, fill=tk.Y)

            # ── Col 3: Date ──────────────────────────────────────
            date_col = tk.Frame(row, bg=row_bg, width=columns[3][1], height=32)
            date_col.pack_propagate(False)
            date_col.pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(date_col, text=date_str,
                     font=theme.get_font(11),
                     fg=SUB_FG, bg=row_bg, anchor="w"
                     ).pack(side=tk.LEFT, fill=tk.Y)

            # ── Col 4: Time (monospace) ──────────────────────────
            time_col = tk.Frame(row, bg=row_bg, width=columns[4][1], height=32)
            time_col.pack_propagate(False)
            time_col.pack(side=tk.LEFT)
            
            time_text = f"{start}  —  {end}"
            tk.Label(time_col, text=time_text,
                     font=("Menlo", 11),
                     fg="#94A3B8", bg=row_bg, anchor="w"
                     ).pack(side=tk.LEFT, fill=tk.Y)

            # Row separator
            tk.Frame(table_frame, bg=BORDER, height=1).pack(fill=tk.X, padx=16)