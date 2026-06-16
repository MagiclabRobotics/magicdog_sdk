#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog navigation GUI — SdkTransportMode::GrpcOnly (WiFi / robot AP).

- Motion: gait, tricks, joystick (linear / angular velocity)
- SLAM: mapping, map load/save/delete
- Navigation & Map: workflow, occupancy grid, click-to-set pose/goal, navigate
- Video: RTSP preview (default rtsp://<robot-ip>:8082)
- Audio: volume, TTS, voice config (gRPC)
- Display: face expressions get/set (gRPC)
- Sensor: open/close hardware sensors (gRPC)
"""

from __future__ import annotations

import os
import re
import socket

import argparse
import logging
import math
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox, ttk
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

import numpy as np

# Prefer SDK build output next to magicdog_sdk/
_SDK_BUILD = Path(__file__).resolve().parents[2] / "build"
if _SDK_BUILD.is_dir():
    sys.path.insert(0, str(_SDK_BUILD))

try:
    import magicdog_python as magicdog
except ImportError as exc:
    raise SystemExit(
        "Cannot import magicdog_python. Build the SDK and run:\n"
        "  export PYTHONPATH=/path/to/magicdog_sdk/build:$PYTHONPATH\n"
        f"  ({exc})"
    ) from exc

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrow

try:
    import cv2
    from PIL import Image, ImageTk

    cv2.setNumThreads(1)
    _HAS_RTSP_DEPS = True
except ImportError:
    _HAS_RTSP_DEPS = False

# UI / matplotlib: prefer fonts with CJK coverage (Chinese labels in this app)
_CJK_FONT_CANDIDATES = (
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "Source Han Sans SC",
    "Source Han Sans CN",
    "WenQuanYi Micro Hei",
    "WenQuanYi Zen Hei",
    "Droid Sans Fallback",
    "Microsoft YaHei",
    "PingFang SC",
    "Segoe UI",
    "Arial Unicode MS",
)
_LATIN_UI_FALLBACK = ("DejaVu Sans", "Liberation Sans", "Ubuntu", "Cantarell")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def _yview_scroll_dy(widget: tk.Widget, dy: int) -> None:
    """Scroll by vertical pixel delta (Tk Text/Listbox only accept units/pages)."""
    if not dy:
        return
    if isinstance(widget, tk.Canvas):
        widget.yview_scroll(-dy, "units")
        return
    try:
        line_h = max(tkfont.Font(font=widget.cget("font")).metrics("linespace"), 1)
    except tk.TclError:
        line_h = 16
    units = int(round(dy / line_h))
    if units == 0:
        units = 1 if dy > 0 else -1
    widget.yview_scroll(-units, "units")


def bind_content_drag_scroll(
    widget: tk.Widget, *, target: Optional[tk.Widget] = None, threshold: int = 0
) -> None:
    """Hold left button and drag vertically to scroll (content area)."""
    scroll_target = target or widget
    if getattr(widget, "_drag_scroll_bound", False):
        return
    widget._drag_scroll_bound = True
    state = {"y": None, "active": False}

    def _press(event: tk.Event) -> None:
        state["y"] = event.y_root
        state["active"] = threshold == 0

    def _motion(event: tk.Event) -> None:
        if state["y"] is None:
            return
        dy = event.y_root - state["y"]
        if not state["active"]:
            if abs(dy) < threshold:
                return
            state["active"] = True
            if isinstance(scroll_target, tk.Listbox):
                scroll_target.selection_clear(0, tk.END)
        state["y"] = event.y_root
        _yview_scroll_dy(scroll_target, dy)

    def _release(_event: tk.Event) -> None:
        state["y"] = None
        state["active"] = False

    widget.bind("<Button-1>", _press, add="+")
    widget.bind("<B1-Motion>", _motion, add="+")
    widget.bind("<ButtonRelease-1>", _release, add="+")


class DragScrollRail(tk.Canvas):
    """Prominent vertical scroll rail — hold and drag the thumb to scroll."""

    def __init__(self, parent: tk.Widget, theme: "AppTheme", target: tk.Widget, **kwargs) -> None:
        super().__init__(
            parent,
            width=theme.SCROLL_RAIL_W,
            highlightthickness=0,
            bg=theme.SCROLL_RAIL,
            cursor="hand2",
            **kwargs,
        )
        self.theme = theme
        self.target = target
        self._first = 0.0
        self._last = 1.0
        self._drag_y: Optional[int] = None
        self._dragging = False

        target.configure(yscrollcommand=self._set_view)
        self.bind("<Configure>", lambda _e: self._paint())
        self.bind("<Button-1>", self._press)
        self.bind("<B1-Motion>", self._motion)
        self.bind("<ButtonRelease-1>", self._release)

    def _set_view(self, first: str, last: str) -> None:
        self._first = float(first)
        self._last = float(last)
        self._paint()

    def _thumb_geometry(self) -> Tuple[int, int, int]:
        h = max(self.winfo_height(), 1)
        pad = 4
        inner_h = max(h - 2 * pad, 1)
        span = self._last - self._first
        if span >= 0.999:
            return pad, h - pad, inner_h
        thumb_h = max(36, int(span * inner_h))
        thumb_y1 = pad + int(self._first * inner_h)
        thumb_y2 = min(thumb_y1 + thumb_h, h - pad)
        return thumb_y1, thumb_y2, inner_h

    def _paint(self) -> None:
        t = self.theme
        self.delete("all")
        h = max(self.winfo_height(), 1)
        w = max(self.winfo_width(), 1)
        pad = 4
        self.create_rectangle(
            pad,
            pad,
            w - pad,
            h - pad,
            fill=t.SCROLL_TROUGH,
            outline=t.ACCENT,
            width=2,
        )
        span = self._last - self._first
        if span >= 0.999:
            return
        thumb_y1, thumb_y2, _inner_h = self._thumb_geometry()
        color = t.SCROLL_THUMB_ACTIVE if self._dragging else t.SCROLL_THUMB
        self.create_rectangle(
            2,
            thumb_y1,
            w - 2,
            thumb_y2,
            fill=color,
            outline=t.ACCENT_DARK,
            width=2,
        )
        cx = w // 2
        for gy in range(thumb_y1 + 12, thumb_y2 - 8, 9):
            self.create_line(cx - 6, gy, cx + 6, gy, fill="#ffffff", width=2)

    def _press(self, event: tk.Event) -> None:
        span = self._last - self._first
        if span < 0.999:
            thumb_y1, thumb_y2, inner_h = self._thumb_geometry()
            if not (thumb_y1 <= event.y <= thumb_y2):
                frac = max(0.0, min(1.0, (event.y - 4) / max(inner_h, 1) - span / 2))
                self.target.yview_moveto(frac)
        self._dragging = True
        self._drag_y = event.y
        self._paint()

    def _motion(self, event: tk.Event) -> None:
        if self._drag_y is None:
            return
        span = self._last - self._first
        if span >= 0.999:
            return
        h = max(self.winfo_height(), 1)
        pad = 4
        inner_h = max(h - 2 * pad, 1)
        thumb_h = max(36, int(span * inner_h))
        travel = max(inner_h - thumb_h, 1)
        rel_y = event.y - pad - thumb_h / 2
        rel_y = max(0.0, min(float(travel), rel_y))
        self.target.yview_moveto(rel_y / travel)
        self._drag_y = event.y

    def _release(self, _event: tk.Event) -> None:
        self._dragging = False
        self._drag_y = None
        self._paint()


class AppTheme:
    """Shared colors and ttk styles for a light, card-based layout."""

    BG = "#e6ecf3"
    SURFACE = "#ffffff"
    SURFACE_ALT = "#f3f6fa"
    BORDER = "#c5d0de"
    BORDER_LIGHT = "#dce4ee"
    TEXT = "#0f172a"
    TEXT_MUTED = "#64748b"
    TEXT_HINT = "#94a3b8"
    ACCENT = "#3b6fd9"
    ACCENT_DARK = "#2f5bb5"
    ACCENT_SOFT = "#e8f0fe"
    ACCENT_MUTED = "#93b4f0"
    SUCCESS = "#0d9488"
    SUCCESS_SOFT = "#ccfbf1"
    DANGER = "#dc2626"
    DANGER_SOFT = "#fee2e2"
    WARN = "#d97706"
    WARN_SOFT = "#fef3c7"
    LOG_BG = "#111827"
    LOG_FG = "#e5e7eb"
    LOG_BORDER = "#1f2937"
    STICK_BASE = "#1a2332"
    STICK_RING = "#3d4f66"
    STICK_RING_INNER = "#2a3548"
    STICK_KNOB = "#4f8ef7"
    STICK_KNOB_RING = "#93c5fd"
    STICK_KNOB_HI = "#7eb3ff"
    MAP_BG = "#1e293b"
    HEADER_BAR = "#2f5bb5"
    HEADER_BAR_HI = "#4a7fe0"
    PILL_IDLE = "#94a3b8"
    SCROLL_THUMB = "#2563eb"
    SCROLL_THUMB_ACTIVE = "#1d4ed8"
    SCROLL_TROUGH = "#bfdbfe"
    SCROLL_RAIL = "#93c5fd"
    SCROLL_WIDTH = 20
    SCROLL_RAIL_W = 26

    # Point sizes (tk / ttk) — compact layout
    SZ_UI = 10
    SZ_UI_SM = 9
    SZ_UI_MD = 10
    SZ_UI_BOLD = 10
    SZ_TITLE = 15
    SZ_SUBTITLE = 9
    SZ_MONO = 9
    SZ_MAP_TICK = 9
    SZ_MAP_TITLE = 11

    # Layout spacing
    PAD_OUTER = 6
    PAD_TAB = 4
    PAD_FRAME = 6
    PAD_INNER = 5
    PAD_ROW = 3
    INFO_WRAP = 620
    JOY_SIZE = 104
    LOG_LINES = 3
    CARD_RADIUS_HI = 1  # highlightthickness for faux card border

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        tk_families = set(tkfont.families())
        self.family = self._pick_font_family(tk_families)
        self.mpl_family = self._pick_mpl_font_family(tk_families, self.family)
        self.mono_family = self._pick_mono_family(tk_families)
        self._configure_matplotlib()
        self.font_ui = self._font(self.SZ_UI)
        self.font_ui_sm = self._font(self.SZ_UI_SM)
        self.font_desc = self._font(self.SZ_UI_MD)
        self.font_ui_bold = self._font(self.SZ_UI_BOLD, weight="bold")
        self.font_title = self._font(self.SZ_TITLE, weight="bold")
        self.font_subtitle = self._font(self.SZ_SUBTITLE)
        self.font_mono = tkfont.Font(
            root=root, family=self.mono_family, size=self.SZ_MONO
        )

    def _font(self, size: int, weight: str = "normal") -> tkfont.Font:
        return tkfont.Font(root=self.root, family=self.family, size=size, weight=weight)

    def _tk_font_has_cjk(self, family: str) -> bool:
        try:
            probe = tkfont.Font(root=self.root, family=family, size=12)
            return probe.measure("\u4e2d\u6587") > 4
        except tk.TclError:
            return False

    @staticmethod
    def _looks_like_cjk_family(name: str) -> bool:
        keys = ("CJK", "Hei", "WenQuanYi", "Noto Sans", "Source Han", "PingFang", "YaHei", "AR PL")
        return any(k in name for k in keys)

    def _pick_font_family(self, families: set[str]) -> str:
        for name in _CJK_FONT_CANDIDATES:
            if name in families and self._tk_font_has_cjk(name):
                logging.info("UI font: %s", name)
                return name
        for name in sorted(families):
            if self._looks_like_cjk_family(name) and self._tk_font_has_cjk(name):
                logging.info("UI font: %s", name)
                return name
        for name in _LATIN_UI_FALLBACK:
            if name in families:
                logging.warning(
                    "No CJK UI font found; install fonts-noto-cjk or wenquanyi. "
                    "Using %s (Chinese text may show tofu).",
                    name,
                )
                return name
        try:
            return tkfont.nametofont("TkDefaultFont").actual("family")
        except tk.TclError:
            return "sans-serif"

    @staticmethod
    def _mpl_font_available(name: str) -> bool:
        try:
            from matplotlib import font_manager as fm

            wanted = name.lower()
            for entry in fm.fontManager.ttflist:
                if entry.name.lower() == wanted:
                    return True
            return False
        except Exception:
            return False

    def _pick_mpl_font_family(self, tk_families: set[str], ui_family: str) -> str:
        if self._mpl_font_available(ui_family):
            return ui_family
        for name in _CJK_FONT_CANDIDATES:
            if name in tk_families and self._mpl_font_available(name):
                logging.info("Matplotlib font: %s", name)
                return name
        for name in _CJK_FONT_CANDIDATES:
            if self._mpl_font_available(name):
                logging.info("Matplotlib font: %s", name)
                return name
        logging.info("Matplotlib font: DejaVu Sans (fallback)")
        return "DejaVu Sans"

    def _configure_matplotlib(self) -> None:
        try:
            import matplotlib.pyplot as plt

            plt.rcParams["font.sans-serif"] = [
                self.mpl_family,
                "Noto Sans CJK SC",
                "WenQuanYi Micro Hei",
                "DejaVu Sans",
                "sans-serif",
            ]
            plt.rcParams["axes.unicode_minus"] = False
        except Exception as exc:
            logging.debug("matplotlib font setup: %s", exc)

    def _pick_mono_family(self, families: set[str]) -> str:
        for name in (
            "Noto Sans Mono CJK SC",
            "Source Han Mono SC",
            "WenQuanYi Micro Hei Mono",
            "JetBrains Mono",
            "Fira Code",
            "DejaVu Sans Mono",
            "Ubuntu Mono",
            "Liberation Mono",
            "Consolas",
        ):
            if name in families and self._tk_font_has_cjk(name):
                return name
        if self._tk_font_has_cjk(self.family):
            return self.family
        for name in ("DejaVu Sans Mono", "Ubuntu Mono", "Liberation Mono"):
            if name in families:
                return name
        return self.family

    def apply(self) -> None:
        self.root.configure(bg=self.BG)
        self.root.option_add("*Font", (self.family, self.SZ_UI))
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=self.BG, foreground=self.TEXT, font=self.font_ui)
        style.configure("TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.SURFACE)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT, font=self.font_ui)
        style.configure(
            "Card.TLabel", background=self.SURFACE, foreground=self.TEXT, font=self.font_ui
        )
        style.configure(
            "Muted.TLabel", background=self.BG, foreground=self.TEXT_MUTED, font=self.font_ui
        )
        style.configure(
            "CardMuted.TLabel",
            background=self.SURFACE,
            foreground=self.TEXT_MUTED,
            font=self.font_ui,
        )
        style.configure(
            "Hint.TLabel", background=self.BG, foreground=self.TEXT_HINT, font=self.font_ui_sm
        )
        style.configure(
            "CardHint.TLabel",
            background=self.SURFACE,
            foreground=self.TEXT_HINT,
            font=self.font_ui_sm,
        )
        style.configure(
            "Title.TLabel", background=self.BG, font=self.font_title, foreground=self.TEXT
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BG,
            font=self.font_subtitle,
            foreground=self.TEXT_HINT,
        )
        style.configure(
            "TLabelframe",
            background=self.SURFACE,
            bordercolor=self.BORDER,
            relief="solid",
            borderwidth=1,
            padding=(4, 3),
        )
        style.configure(
            "TLabelframe.Label",
            background=self.SURFACE,
            foreground=self.ACCENT_DARK,
            font=self.font_ui_bold,
        )
        style.configure("TButton", font=self.font_ui, padding=(8, 4))
        style.map("TButton", background=[("active", self.SURFACE_ALT)])
        style.configure(
            "Accent.TButton",
            background=self.ACCENT,
            foreground="#ffffff",
            font=self.font_ui_bold,
            padding=(10, 4),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", self.ACCENT_DARK),
                ("pressed", self.ACCENT_DARK),
                ("disabled", self.ACCENT_MUTED),
            ],
            foreground=[("disabled", "#f8fafc")],
        )
        style.configure(
            "Danger.TButton",
            background=self.DANGER,
            foreground="#ffffff",
            font=self.font_ui_bold,
            padding=(10, 4),
            borderwidth=0,
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#b91c1c"), ("pressed", "#b91c1c"), ("disabled", "#fca5a5")],
        )
        style.configure(
            "Muted.TButton",
            foreground=self.TEXT_MUTED,
            background=self.SURFACE_ALT,
        )
        style.map("Muted.TButton", background=[("active", self.BORDER_LIGHT)])
        style.configure(
            "TEntry",
            fieldbackground=self.SURFACE,
            font=self.font_ui,
            padding=4,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER_LIGHT,
            darkcolor=self.BORDER,
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", self.ACCENT), ("!focus", self.BORDER)],
            lightcolor=[("focus", self.ACCENT_MUTED)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.SURFACE,
            font=self.font_ui,
            padding=4,
            bordercolor=self.BORDER,
        )
        style.configure(
            "TRadiobutton",
            background=self.SURFACE,
            font=self.font_ui,
        )
        style.map("TRadiobutton", background=[("active", self.SURFACE)])
        style.configure(
            "TCheckbutton",
            background=self.SURFACE,
            font=self.font_ui,
        )
        style.map("TCheckbutton", background=[("active", self.SURFACE)])
        style.configure(
            "Horizontal.TScale",
            background=self.SURFACE,
            troughcolor=self.SURFACE_ALT,
            bordercolor=self.BORDER,
        )
        style.configure(
            "TNotebook",
            background=self.SURFACE,
            borderwidth=0,
            tabmargins=[2, 4, 2, 0],
        )
        style.configure(
            "TNotebook.Tab",
            padding=(10, 5),
            font=self.font_ui_bold,
            background=self.BG,
            borderwidth=1,
            relief="flat",
        )
        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", self.SURFACE),
                ("active", self.SURFACE_ALT),
                ("!selected", self.BG),
            ],
            foreground=[
                ("selected", self.ACCENT_DARK),
                ("active", self.TEXT),
                ("!selected", self.TEXT_MUTED),
            ],
            expand=[("selected", [1, 1, 1, 0])],
        )
        style.configure(
            "TScrollbar",
            background=self.SCROLL_THUMB,
            troughcolor=self.SCROLL_TROUGH,
            bordercolor=self.BORDER,
            arrowcolor=self.ACCENT,
            width=self.SCROLL_WIDTH,
            arrowsize=11,
            gripcount=0,
        )
        style.map(
            "TScrollbar",
            background=[
                ("active", self.SCROLL_THUMB_ACTIVE),
                ("pressed", self.ACCENT_DARK),
                ("!active", self.SCROLL_THUMB),
            ],
        )
        style.configure(
            "Scroll.TScrollbar",
            background=self.SCROLL_THUMB,
            troughcolor=self.SCROLL_TROUGH,
            bordercolor=self.BORDER,
            arrowcolor=self.ACCENT,
            width=self.SCROLL_WIDTH,
            arrowsize=11,
            gripcount=0,
        )
        style.map(
            "Scroll.TScrollbar",
            background=[
                ("active", self.SCROLL_THUMB_ACTIVE),
                ("pressed", self.ACCENT_DARK),
                ("!active", self.SCROLL_THUMB),
            ],
        )
        style.configure(
            "Stick.TLabel",
            background=self.SURFACE_ALT,
            foreground=self.TEXT_MUTED,
            font=self.font_ui_sm,
        )
        style.configure(
            "StickValue.TLabel",
            background=self.SURFACE_ALT,
            foreground=self.TEXT_HINT,
            font=self.font_ui,
        )
        style.configure(
            "Step.TLabel",
            background=self.ACCENT_SOFT,
            foreground=self.ACCENT,
            font=self.font_ui_bold,
        )
        style.configure(
            "StepTitle.TLabel",
            background=self.SURFACE,
            foreground=self.TEXT,
            font=self.font_ui_bold,
        )
        style.configure(
            "StepDetail.TLabel",
            background=self.SURFACE,
            foreground=self.TEXT_MUTED,
            font=self.font_ui_sm,
        )
        style.configure(
            "FlowHint.TLabel",
            background=self.SURFACE_ALT,
            foreground=self.TEXT_MUTED,
            font=self.font_ui_sm,
        )
        for name, fg in (
            ("StatusOk.TLabel", self.SUCCESS),
            ("StatusBad.TLabel", self.DANGER),
            ("StatusIdle.TLabel", self.TEXT_HINT),
            ("StatusWarn.TLabel", self.WARN),
        ):
            style.configure(
                name,
                foreground=fg,
                font=self.font_ui_bold,
                background=self.SURFACE,
            )

    def inset_panel(
        self,
        parent: tk.Widget,
        *,
        fill: str = tk.X,
        expand: bool = False,
        pady: Optional[int] = None,
        padx: Optional[int] = None,
        bg: Optional[str] = None,
    ) -> tk.Frame:
        """Light inset block for grouping related controls."""
        if pady is None:
            pady = self.PAD_ROW
        if padx is None:
            padx = self.PAD_INNER
        panel_bg = bg or self.SURFACE_ALT
        shell = tk.Frame(parent, bg=self.BORDER, highlightthickness=0)
        shell.pack(fill=fill, expand=expand, padx=padx, pady=pady)
        inner = tk.Frame(shell, bg=panel_bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        return inner

    def card_shell(
        self, parent: tk.Widget, *, fill: str = tk.X, expand: bool = False, pady: Optional[int] = None
    ) -> tk.Frame:
        """White card with subtle border."""
        if pady is None:
            pady = self.PAD_ROW
        shell = tk.Frame(
            parent,
            bg=self.SURFACE,
            highlightbackground=self.BORDER,
            highlightthickness=self.CARD_RADIUS_HI,
        )
        shell.pack(fill=fill, expand=expand, padx=0, pady=pady)
        return shell

    def info_box(
        self, parent: tk.Widget, text: str, wraplength: Optional[int] = None
    ) -> tk.Label:
        if wraplength is None:
            wraplength = self.INFO_WRAP
        shell = tk.Frame(parent, bg=self.BORDER, highlightthickness=0)
        shell.pack(fill=tk.X, padx=self.PAD_INNER, pady=(0, self.PAD_ROW))
        outer = tk.Frame(shell, bg=self.SURFACE_ALT)
        outer.pack(fill=tk.X, padx=1, pady=1)
        stripe = tk.Frame(outer, bg=self.ACCENT, width=3)
        stripe.pack(side=tk.LEFT, fill=tk.Y)
        body = tk.Frame(
            outer,
            bg=self.ACCENT_SOFT,
            highlightbackground=self.ACCENT_MUTED,
            highlightthickness=1,
        )
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lbl = tk.Label(
            body,
            text=text,
            bg=self.ACCENT_SOFT,
            fg=self.TEXT_MUTED,
            font=self.font_ui_sm,
            wraplength=wraplength,
            justify=tk.LEFT,
            anchor=tk.W,
        )
        lbl.pack(fill=tk.X, padx=self.PAD_INNER, pady=self.PAD_ROW)
        return lbl

    def style_listbox(self, lb: tk.Listbox) -> None:
        lb.configure(
            bg=self.SURFACE,
            fg=self.TEXT,
            selectbackground=self.ACCENT,
            selectforeground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
            activestyle="none",
            borderwidth=0,
        )

    def make_pill(
        self,
        parent: tk.Widget,
        text: str,
        *,
        bg: str,
        fg: str = "#f8fafc",
    ) -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=self.font_ui_bold,
            padx=8,
            pady=2,
        )

    def paned_config(self, paned: tk.PanedWindow) -> None:
        paned.configure(
            bg=self.BORDER,
            sashwidth=5,
            sashrelief=tk.FLAT,
            showhandle=False,
            opaqueresize=True,
            borderwidth=0,
        )

    def mount_scroll_rail(self, body: tk.Frame, target: tk.Widget) -> DragScrollRail:
        rail_wrap = tk.Frame(body, bg=self.SCROLL_RAIL, width=self.SCROLL_RAIL_W)
        rail_wrap.pack(side=tk.RIGHT, fill=tk.Y)
        rail_wrap.pack_propagate(False)
        rail = DragScrollRail(rail_wrap, self, target)
        rail.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        return rail

    def scroll_body(self, parent: tk.Widget, *, border: bool = True) -> tk.Frame:
        """Row body: pack scrollable content LEFT, then mount_scroll_rail(body, target)."""
        if border:
            shell = tk.Frame(
                parent,
                bg=self.BORDER,
                highlightbackground=self.BORDER,
                highlightthickness=1,
            )
            shell.pack(fill=tk.BOTH, expand=True)
            inner = tk.Frame(shell, bg=self.SURFACE)
            inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        else:
            inner = tk.Frame(parent, bg=self.SURFACE)
            inner.pack(fill=tk.BOTH, expand=True)
        body = tk.Frame(inner, bg=self.SURFACE_ALT)
        body.pack(fill=tk.BOTH, expand=True)
        return body

    def listbox_panel(self, parent: tk.Widget, *, height: int) -> Tuple[tk.Frame, tk.Listbox]:
        """Listbox with bordered panel and drag scroll rail."""
        panel = tk.Frame(
            parent,
            bg=self.SURFACE,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        body = tk.Frame(panel, bg=self.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=self.PAD_ROW, pady=self.PAD_ROW)

        lb = tk.Listbox(body, height=height, font=self.font_ui)
        self.style_listbox(lb)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0), pady=2)

        self.mount_scroll_rail(body, lb)
        bind_content_drag_scroll(lb, threshold=8)
        return panel, lb


# --- Gait / trick presets for UI (label, enum, description) ---

ChoiceRow = Tuple[str, object, str]

# (state key, UI title, description)
SENSOR_HW_ROWS: List[Tuple[str, str, str]] = [
    (
        "channel",
        "数据通道",
        "open_channel_switch / close_channel_switch；打开其它传感器前通常需先开启通道。",
    ),
    (
        "laser_scan",
        "激光雷达 · LaserScan",
        "OpenLaserScan / CloseLaserScan",
    ),
    (
        "rgbd_camera",
        "RGBD 深度相机",
        "OpenRgbdCamera / CloseRgbdCamera",
    ),
    (
        "binocular_camera",
        "双目相机",
        "OpenBinocularCamera / CloseBinocularCamera",
    ),
]

GAIT_CHOICES: List[ChoiceRow] = [
    (
        "Stand (recovery) · 恢复站立",
        magicdog.GaitMode.GAIT_STAND_R,
        "位置控站立（RecoveryStand）。上电后常用初始步态，适合静止与起身。",
    ),
    (
        "Balance stand · 力控站立",
        magicdog.GaitMode.GAIT_STAND_B,
        "力控平衡站立（BalanceStand）。可小幅调整姿态，适合展示或轻扰动环境。",
    ),
    (
        "Down climb stairs (nav) · 导航盲走",
        magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS,
        "下楼梯/盲走/慢跑组合步态。建图、定位、导航前通常需切换到此步态。",
    ),
    (
        "Passive · 卸力",
        magicdog.GaitMode.GAIT_PASSIVE,
        "被动/卸力（Drop）：关闭电机使能，关节可自由摆动。维护或搬运时使用。",
    ),
    (
        "Run fast · 快跑",
        magicdog.GaitMode.GAIT_RUN_FAST,
        "快速奔跑。平地高速移动；注意周围障碍与电池余量。",
    ),
    (
        "RL terrain · 全地形",
        magicdog.GaitMode.GAIT_RL_TERRAIN,
        "强化学习全地形步态。适应复杂路面，算力与能耗高于常规步态。",
    ),
]

TRICK_CHOICES: List[ChoiceRow] = [
    ("— · 无", magicdog.TrickAction.ACTION_NONE, "不执行特技；点击 Execute 无效果。"),
    ("Wiggle hip · 扭臀", magicdog.TrickAction.ACTION_WIGGLE_HIP, "扭屁股。娱乐动作。"),
    ("Swing body · 摆身", magicdog.TrickAction.ACTION_SWING_BODY, "摆身体。"),
    ("Stretch · 伸懒腰", magicdog.TrickAction.ACTION_STRETCH, "伸懒腰。热身、表演前常用。"),
    ("Stomp · 跺脚", magicdog.TrickAction.ACTION_STOMP, "跺脚。"),
    ("Jump jack · 开合跳", magicdog.TrickAction.ACTION_JUMP_JACK, "开合跳。"),
    ("Space walk · 太空步", magicdog.TrickAction.ACTION_SPACE_WALK, "太空步。"),
    ("Imitate · 模仿", magicdog.TrickAction.ACTION_IMITATE, "模仿。"),
    ("Shake head · 摇头", magicdog.TrickAction.ACTION_SHAKE_HEAD, "摇头。短时娱乐动作。"),
    ("Push up · 俯卧撑", magicdog.TrickAction.ACTION_PUSH_UP, "俯卧撑。健身类动作。"),
    ("Cheer up · 欢呼", magicdog.TrickAction.ACTION_CHEER_UP, "加油/欢呼。"),
    ("High fives · 击掌", magicdog.TrickAction.ACTION_HIGH_FIVES, "击掌/挥手。互动展示用。"),
    ("Scratch · 抓挠", magicdog.TrickAction.ACTION_SCRATCH, "抓挠。"),
    ("High jump · 跳高", magicdog.TrickAction.ACTION_HIGH_JUMP, "跳高。跳跃类动作。"),
    ("Swing dance · 摇摆舞", magicdog.TrickAction.ACTION_SWING_DANCE, "摇摆舞。舞蹈类动作。"),
    ("Leap frog · 蛙跳", magicdog.TrickAction.ACTION_LEAP_FROG, "蛙跳。"),
    ("Back flip · 后空翻", magicdog.TrickAction.ACTION_BACK_FLIP, "后空翻。高难度，需足够空间。"),
    ("Front flip · 前空翻", magicdog.TrickAction.ACTION_FRONT_FLIP, "前空翻。高难度，需足够空间。"),
    (
        "Spin jump left · 左旋跳",
        magicdog.TrickAction.ACTION_SPIN_JUMP_LEFT,
        "左旋转跳（约 70°）。",
    ),
    (
        "Spin jump right · 右旋跳",
        magicdog.TrickAction.ACTION_SPIN_JUMP_RIGHT,
        "右旋转跳（约 70°）。",
    ),
    ("Jump front · 前跳", magicdog.TrickAction.ACTION_JUMP_FRONT, "向前跳（约 0.5 m）。"),
    ("Act cute · 撒娇", magicdog.TrickAction.ACTION_ACT_CUTE, "撒娇。娱乐动作。"),
    ("Boxing · 拳击", magicdog.TrickAction.ACTION_BOXING, "拳击。"),
    ("Side somersault · 侧空翻", magicdog.TrickAction.ACTION_SIDE_SOMERSAULT, "侧空翻。高难度。"),
    ("Random dance · 随机舞", magicdog.TrickAction.ACTION_RANDOM_DANCE, "随机跳舞。"),
    (
        "Left side somersault · 左侧翻",
        magicdog.TrickAction.ACTION_LEFT_SIDE_SOMERSAULT,
        "左侧空翻。高难度。",
    ),
    (
        "Right side somersault · 右侧翻",
        magicdog.TrickAction.ACTION_RIGHT_SIDE_SOMERSAULT,
        "右侧空翻。高难度。",
    ),
    ("Dance 2 · 舞蹈2", magicdog.TrickAction.ACTION_DANCE2, "舞蹈 2。"),
    (
        "Emergency stop · 急停",
        magicdog.TrickAction.ACTION_EMERGENCY_STOP,
        "急停。立即打断当前动作，异常时优先使用。",
    ),
    ("Lie down · 趴下", magicdog.TrickAction.ACTION_LIE_DOWN, "趴下。展示结束或低姿态保护。"),
    (
        "Recovery stand · 起立",
        magicdog.TrickAction.ACTION_RECOVERY_STAND,
        "起立（Stand up）。趴下后恢复站立。",
    ),
    ("Happy New Year · 拜年", magicdog.TrickAction.ACTION_HAPPY_NEW_YEAR, "拜年/新年问候。"),
    ("Come here (slow) · 过来", magicdog.TrickAction.ACTION_SLOW_GO_FRONT, "慢速前进（过来）。"),
    ("Go back (slow) · 后退", magicdog.TrickAction.ACTION_SLOW_GO_BACK, "慢速后退。"),
    ("Back home · 回家", magicdog.TrickAction.ACTION_BACK_HOME, "回家。"),
    ("Leave home · 离家", magicdog.TrickAction.ACTION_LEAVE_HOME, "离家。"),
    ("Turn around · 转身", magicdog.TrickAction.ACTION_TURN_AROUND, "转身。"),
    ("Dance · 跳舞", magicdog.TrickAction.ACTION_DANCE, "跳舞。"),
    ("Roll about · 打滚", magicdog.TrickAction.ACTION_ROLL_ABOUT, "打滚。"),
    ("Shake right hand · 挥右手", magicdog.TrickAction.ACTION_SHAKE_RIGHT_HAND, "握/挥右手。"),
    ("Shake left hand · 挥左手", magicdog.TrickAction.ACTION_SHAKE_LEFT_HAND, "握/挥左手。"),
    ("Sit down · 坐下", magicdog.TrickAction.ACTION_SIT_DOWN, "坐下，直至切换步态或其它动作。"),
]

# All GaitMode numeric values from magic_type.h (incl. robot-only modes not in pybind).
GAIT_NAME_BY_INT: dict[int, str] = {
    -1: "GAIT_UNKNOWN",
    0: "GAIT_PASSIVE",
    2: "GAIT_STAND_R",
    3: "GAIT_STAND_B",
    8: "GAIT_RUN_FAST",
    9: "GAIT_DOWN_CLIMB_STAIRS",
    10: "GAIT_TROT",
    11: "GAIT_PRONK",
    12: "GAIT_BOUND",
    14: "GAIT_AMBLE",
    29: "GAIT_CRAWL",
    30: "GAIT_LOWLEVL_SDK",
    39: "GAIT_WALK",
    56: "GAIT_UP_CLIMB_STAIRS",
    99: "GAIT_DEFAULT",
    110: "GAIT_RL_TERRAIN",
    111: "GAIT_RL_FALL_RECOVERY",
    112: "GAIT_RL_HAND_STAND",
    113: "GAIT_RL_FOOT_STAND",
    1001: "GAIT_ENTER_RL",
    9999: "GAIT_NONE",
}

# GetGait reads SDK cache fed by robot state stream; 9999/-1 often means "not reported".
GAIT_SENTINEL_IDS = frozenset({-1, 9999})


def _gait_is_sentinel(gait: object) -> bool:
    val, _ = _gait_key(gait)
    return val in GAIT_SENTINEL_IDS


def _enum_name(val: object) -> str:
    if val is None:
        return "—"
    name = getattr(val, "name", None)
    if name:
        return str(name)
    return str(val)


def _lookup_error_code(error_code: int) -> str:
    """Resolve fault code via SDK magic_err.h error_code_map."""
    if hasattr(magicdog, "lookup_error_code"):
        return magicdog.lookup_error_code(int(error_code))
    fault = magicdog.Fault()
    fault.error_code = int(error_code)
    if hasattr(fault, "error_name"):
        return fault.error_name
    key = int(error_code) & 0xFFFF
    return f"Unknown error (0x{key:04X})"


def _format_fault_line(fault: object) -> str:
    code = int(fault.error_code)
    code_hex = f"0x{code & 0xFFFF:04X}"
    known = _lookup_error_code(code)
    extra = (fault.error_message or "").strip().replace("\n", " ")
    if extra and extra != known:
        if len(extra) > 52:
            extra = extra[:49] + "..."
        return f"  {code_hex} {known}\n      {extra}"
    return f"  {code_hex} {known}"


def _format_motion_robot_state(
    connected: bool,
    state: Optional[object],
    localization: Optional[object],
) -> str:
    if not connected:
        return "未连接\n\nConnect 后显示 RobotState\n(来自 gRPC subscribeRobotState)"
    lines = ["RobotState", "—" * 38]
    if state is None:
        lines.append("等待状态流首包…")
    else:
        bms = state.bms_data
        lines.extend(
            [
                f"Battery  {bms.battery_percentage:.1f}%",
                f"Health   {bms.battery_health:.1f}",
                f"BMS      {_enum_name(bms.battery_state)}",
                f"Supply   {_enum_name(bms.power_supply_status)}",
            ]
        )
        faults = list(state.faults or [])
        lines.append(f"Faults   {len(faults)}")
        for fault in faults[:8]:
            lines.append(_format_fault_line(fault))
        if len(faults) > 8:
            lines.append(f"  … +{len(faults) - 8}")
    lines.append("")
    lines.append("Localization")
    if localization is None:
        lines.append("  —")
    elif localization.is_localization:
        p = localization.pose.position
        y = localization.pose.orientation[2]
        lines.append(f"  OK  x={p[0]:.2f} y={p[1]:.2f} yaw={y:.2f}")
    else:
        lines.append("  Not localized")
    lines.append("")
    lines.append("~500ms · gRPC stream")
    return "\n".join(lines)


def _gait_fallback_enum(sentinel_val: Optional[int], last_gait: Optional[object]):
    """When GetGait returns sentinel, guess display gait (9999 → recovery stand is common)."""
    if last_gait is not None and not _gait_is_sentinel(last_gait):
        return last_gait
    if sentinel_val == 9999:
        return magicdog.GaitMode.GAIT_STAND_R
    return None


def _choice_by_label(choices: List[ChoiceRow], label: str) -> Optional[ChoiceRow]:
    for row in choices:
        if row[0] == label:
            return row
    return None


def _choice_value(choices: List[ChoiceRow], label: str) -> object:
    row = _choice_by_label(choices, label)
    return row[1] if row else choices[0][1]


def _choice_desc(choices: List[ChoiceRow], label: str) -> str:
    row = _choice_by_label(choices, label)
    return row[2] if row else choices[0][2]


def _choice_by_value(choices: List[ChoiceRow], value: object) -> Optional[ChoiceRow]:
    for row in choices:
        if row[1] == value:
            return row
    return None


def _gait_key(gait: object) -> Tuple[Optional[int], str]:
    """Resolve robot gait to (int value, ASCII enum name). Prefer int map over pybind .name."""
    if gait is None:
        return None, "GAIT_NONE"
    try:
        val = int(gait)
        return val, GAIT_NAME_BY_INT.get(val, f"GAIT_VALUE_{val}")
    except (TypeError, ValueError):
        pass
    if isinstance(gait, int):
        return gait, GAIT_NAME_BY_INT.get(gait, f"GAIT_VALUE_{gait}")
    name = getattr(gait, "name", None)
    if name and str(name).isascii() and str(name).startswith("GAIT_"):
        return None, str(name)
    text = str(gait)
    if "." in text:
        suffix = text.split(".", 1)[-1]
        if suffix.isascii():
            return None, suffix
    return None, "GAIT_UNKNOWN"


def _choice_by_gait(gait: object) -> Optional[ChoiceRow]:
    val, name = _gait_key(gait)
    for row in GAIT_CHOICES:
        if row[1] == gait:
            return row
        row_name = getattr(row[1], "name", None)
        if row_name and row_name == name:
            return row
        if val is not None:
            try:
                if int(row[1]) == val:
                    return row
            except (TypeError, ValueError):
                pass
    return None


def _gait_enum_short_name(gait: object) -> str:
    return _gait_key(gait)[1]


def _gait_ui_label(gait: object) -> str:
    row = _choice_by_gait(gait)
    if row:
        return row[0]
    val, name = _gait_key(gait)
    if val is not None and name.startswith("GAIT_"):
        return name
    return name


def _gait_log_line(gait: object, last_gait: Optional[object] = None) -> str:
    """ASCII-only summary for Log / logging."""
    val, name = _gait_key(gait)
    if _gait_is_sentinel(gait):
        fb = _gait_fallback_enum(val, last_gait)
        if fb is not None:
            fv, fn = _gait_key(fb)
            return (
                f"GetGait id={val} ({name}), not synced; "
                f"showing {fn} (id={fv}) from last SetGait"
            )
        return f"GetGait id={val} ({name}), cache not synced"
    if val is not None:
        return f"{name} (id={val})"
    return name


def _format_gait_status(
    gait: object, last_gait: Optional[object] = None
) -> Tuple[str, Optional[ChoiceRow], bool]:
    """
    Returns (status_line, combobox_row, used_fallback).
    status_line is UI text; combobox_row set when dropdown should sync.
    """
    val, enum_name = _gait_key(gait)
    id_part = f", id={val}" if val is not None else ""
    if not _gait_is_sentinel(gait):
        row = _choice_by_gait(gait)
        label = row[0] if row else _gait_ui_label(gait)
        return f"当前步态：{label}  ({enum_name}{id_part})", row, False

    fb = _gait_fallback_enum(val, last_gait)
    row = _choice_by_gait(fb) if fb is not None else None
    hint_label = row[0] if row else (_gait_ui_label(fb) if fb else "—")
    fb_name = _gait_enum_short_name(fb) if fb is not None else "—"
    fb_val, _ = _gait_key(fb) if fb is not None else (None, "")
    fb_id = f", id={fb_val}" if fb_val is not None else ""
    return (
        f"当前步态：{hint_label}  ({fb_name}{fb_id})  "
        f"[参考；GetGait 返回 {enum_name}{id_part}，非实时]",
        row,
        True,
    )


def _status_ok(status) -> bool:
    return status.code == magicdog.ErrorCode.OK


def _sdk_features_motion_and_slam():
    """Combine SdkFeature flags (works before/after pybind arithmetic() on SdkFeature)."""
    motion = magicdog.SdkFeature.HIGH_LEVEL_MOTION
    slam = magicdog.SdkFeature.SLAM_NAVIGATION
    try:
        return motion | slam
    except TypeError:
        combined = int(motion) | int(slam)
        try:
            return magicdog.SdkFeature(combined)
        except (TypeError, ValueError):
            return magicdog.SdkFeature.ALL


def _image_bytes_to_array(map_image_data) -> Optional[np.ndarray]:
    w, h = map_image_data.width, map_image_data.height
    raw = map_image_data.image
    if hasattr(raw, "__iter__") and not isinstance(raw, (str, bytes)):
        raw = bytes(raw)
    if len(raw) != w * h:
        return None
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
    return arr


def world_to_cell(
    x: float, y: float, origin_xy: Tuple[float, float], resolution: float, height: int
) -> Tuple[int, int]:
    col = int((x - origin_xy[0]) / resolution)
    row = height - 1 - int((y - origin_xy[1]) / resolution)
    return col, row


def _paint_map_legend_icon(
    canvas: tk.Canvas, kind: str, fg: str, arrow_fg: str
) -> None:
    canvas.delete("all")
    if kind == "robot":
        canvas.create_oval(2, 6, 10, 14, fill=fg, outline=fg)
        canvas.create_line(
            11, 10, 24, 10, fill=fg, width=2, arrow=tk.LAST, arrowshape=(6, 8, 3)
        )
    elif kind == "init":
        canvas.create_oval(2, 6, 10, 14, fill=fg, outline="#fef3c7", width=1)
        canvas.create_line(
            11, 10, 24, 10, fill=fg, width=2, arrow=tk.LAST, arrowshape=(6, 8, 3)
        )
    else:
        canvas.create_line(3, 4, 9, 16, fill=fg, width=2)
        canvas.create_line(9, 4, 3, 16, fill=fg, width=2)
        canvas.create_line(
            12, 10, 26, 10, fill=arrow_fg, width=2, arrow=tk.LAST, arrowshape=(6, 8, 3)
        )


class VirtualJoystick(ttk.Frame):
    """Circular analog stick; outputs normalized (x, y) in [-1, 1]. Y up is positive."""

    def __init__(
        self,
        master,
        size: int = 128,
        knob_ratio: float = 0.32,
        label: str = "",
        horizontal_only: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._size = size
        self._cx = size / 2
        self._cy = size / 2
        self._outer_r = size / 2 - 10
        self._knob_r = self._outer_r * knob_ratio
        self._travel = self._outer_r - self._knob_r
        self._horizontal_only = horizontal_only
        self._knob_dx = 0.0
        self._knob_dy = 0.0
        self._dragging = False
        self._value_var = tk.StringVar(value="0.00, 0.00")

        if label:
            ttk.Label(self, text=label, style="Stick.TLabel", wraplength=size + 40).pack(
                pady=(0, 4)
            )
        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            highlightthickness=0,
            bg=AppTheme.STICK_BASE,
            cursor="hand2",
        )
        self.canvas.pack()
        ttk.Label(self, textvariable=self._value_var, style="StickValue.TLabel").pack(
            pady=(4, 0)
        )
        self._draw_base()
        self._draw_knob()
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Leave>", self._on_leave_while_drag)

    def get_values(self) -> Tuple[float, float]:
        if self._travel <= 0:
            return 0.0, 0.0
        x = max(-1.0, min(1.0, self._knob_dx / self._travel))
        y = max(-1.0, min(1.0, -self._knob_dy / self._travel))
        return x, y

    def reset(self) -> None:
        self._knob_dx = 0.0
        self._knob_dy = 0.0
        self._dragging = False
        self._redraw()

    def _draw_base(self) -> None:
        c = self.canvas
        c.delete("base")
        cx, cy, ro = self._cx, self._cy, self._outer_r
        c.create_oval(
            cx - ro - 2,
            cy - ro - 2,
            cx + ro + 2,
            cy + ro + 2,
            outline=AppTheme.STICK_RING_INNER,
            width=1,
            fill="",
            tags="base",
        )
        c.create_oval(
            cx - ro,
            cy - ro,
            cx + ro,
            cy + ro,
            outline=AppTheme.STICK_RING,
            width=2,
            fill=AppTheme.STICK_BASE,
            tags="base",
        )
        c.create_oval(
            cx - ro + 6,
            cy - ro + 6,
            cx + ro - 6,
            cy + ro - 6,
            outline=AppTheme.STICK_RING_INNER,
            width=1,
            fill="",
            tags="base",
        )
        c.create_oval(cx - 2, cy - 2, cx + 2, cy + 2, fill="#64748b", outline="", tags="base")
        if self._horizontal_only:
            c.create_line(
                cx - ro + 4, cy, cx + ro - 4, cy, fill="#334155", width=1, tags="base"
            )

    def _draw_knob(self) -> None:
        c = self.canvas
        c.delete("knob")
        kx = self._cx + self._knob_dx
        ky = self._cy + self._knob_dy
        kr = self._knob_r
        c.create_oval(
            kx - kr,
            ky - kr,
            kx + kr,
            ky + kr,
            outline=AppTheme.STICK_KNOB_RING,
            width=2,
            fill=AppTheme.STICK_KNOB,
            tags="knob",
        )
        hi = kr * 0.35
        c.create_oval(
            kx - hi,
            ky - hi - kr * 0.15,
            kx + hi,
            ky - hi + kr * 0.15,
            fill=AppTheme.STICK_KNOB_HI,
            outline="",
            tags="knob",
        )

    def _redraw(self) -> None:
        self._draw_knob()
        x, y = self.get_values()
        self._value_var.set(f"{x:+.2f}, {y:+.2f}")

    def _pointer_to_offset(self, px: float, py: float) -> None:
        dx = px - self._cx
        dy = py - self._cy
        if self._horizontal_only:
            dy = 0.0
        dist = math.hypot(dx, dy)
        if dist > self._travel and dist > 1e-6:
            scale = self._travel / dist
            dx *= scale
            dy *= scale
        self._knob_dx = dx
        self._knob_dy = dy
        self._redraw()

    def _on_press(self, event) -> None:
        if event.y > self._size:
            return
        self._dragging = True
        self._pointer_to_offset(event.x, event.y)

    def _on_motion(self, event) -> None:
        if not self._dragging:
            return
        self._pointer_to_offset(event.x, event.y)

    def _on_release(self, event) -> None:
        self._dragging = False
        self.reset()

    def _on_leave_while_drag(self, event) -> None:
        if self._dragging:
            self._on_release(event)


class RobotSession:
    """Thread-safe wrapper around MagicRobot (GrpcOnly + motion + SLAM)."""

    def __init__(self) -> None:
        self.robot: Optional[magicdog.MagicRobot] = None
        self.high = None
        self.slam = None
        self.audio = None
        self.display = None
        self.sensor = None
        self._sensor_channel_open = False
        self._sensor_hw: dict[str, bool] = {
            "laser_scan": False,
            "rgbd_camera": False,
            "binocular_camera": False,
        }
        self._lock = threading.Lock()
        self.connected = False
        self.joy_active = False
        self.joy_thread: Optional[threading.Thread] = None
        self.poll_thread: Optional[threading.Thread] = None
        self.poll_running = False
        self.localization: Optional[object] = None
        self.robot_state: Optional[object] = None
        self.nav_status_msg = ""
        self.current_map_name = ""
        self.map_array: Optional[np.ndarray] = None
        self.map_origin = (0.0, 0.0)
        self.map_resolution = 0.05
        self._last_gait: Optional[object] = None

    def remember_gait(self, gait: object) -> None:
        if gait is not None and not _gait_is_sentinel(gait):
            self._last_gait = gait

    def connect(self, local_ip: str, robot_ip: str) -> Tuple[bool, str]:
        with self._lock:
            if self.connected:
                return True, "Already connected"
            self.robot = magicdog.MagicRobot()
            features = _sdk_features_motion_and_slam()
            if not self.robot.initialize_grpc_only(local_ip, features, robot_ip):
                self.robot = None
                return False, "initialize_grpc_only failed"
            st = self.robot.connect()
            if not _status_ok(st):
                self.robot.shutdown()
                self.robot = None
                return False, f"connect failed: {st.message}"
            st = self.robot.set_motion_control_level(magicdog.ControllerLevel.HIGH_LEVEL)
            if not _status_ok(st):
                self.robot.shutdown()
                self.robot = None
                return False, f"set_motion_control_level: {st.message}"
            self.high = self.robot.get_high_level_motion_controller()
            self.slam = self.robot.get_slam_nav_controller()
            self.high.enable_joy_stick()
            audio_note = self._setup_audio()
            display_note = self._setup_display()
            sensor_note = self._setup_sensor()
            self.connected = True
            self._start_poll()
            return True, f"Connected (GrpcOnly). {audio_note} {display_note} {sensor_note}"

    def disconnect(self) -> None:
        with self._lock:
            self._stop_joy()
            self._stop_poll()
            self._teardown_audio()
            self._teardown_display()
            self._teardown_sensor()
            if self.high:
                try:
                    self.high.disable_joy_stick()
                except Exception:
                    pass
            if self.robot:
                try:
                    self.robot.disconnect()
                    self.robot.shutdown()
                except Exception:
                    pass
            self.robot = None
            self.high = None
            self.slam = None
            self.audio = None
            self.display = None
            self.sensor = None
            self._sensor_channel_open = False
            for key in self._sensor_hw:
                self._sensor_hw[key] = False
            self._last_gait = None
            self.robot_state = None
            self.connected = False

    def _start_poll(self) -> None:
        self.poll_running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def _stop_poll(self) -> None:
        self.poll_running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=2.0)
            self.poll_thread = None

    def _poll_loop(self) -> None:
        while self.poll_running:
            try:
                if self.slam:
                    st, loc = self.slam.get_current_localization_info()
                    if _status_ok(st):
                        with self._lock:
                            self.localization = loc
                    st2, nav = self.slam.get_nav_task_status()
                    if _status_ok(st2):
                        with self._lock:
                            self.nav_status_msg = (
                                f"id={nav.id} status={nav.status} {nav.message}"
                            )
                if self.robot:
                    mon = self.robot.get_state_monitor()
                    st3, rs = mon.get_current_state()
                    if _status_ok(st3):
                        with self._lock:
                            self.robot_state = rs
            except Exception as exc:
                logging.debug("poll: %s", exc)
            time.sleep(0.5)

    def run(self, fn: Callable[[], Tuple[bool, str]]) -> Tuple[bool, str]:
        if not self.connected:
            return False, "Not connected"
        try:
            return fn()
        except Exception as exc:
            logging.exception("robot command")
            return False, str(exc)

    def set_gait(self, gait) -> Tuple[bool, str]:
        def _do():
            st = self.high.set_gait(gait)
            ok = _status_ok(st)
            if ok:
                self.remember_gait(gait)
            return ok, st.message

        return self.run(_do)

    def execute_trick(self, trick) -> Tuple[bool, str]:
        if trick == magicdog.TrickAction.ACTION_NONE:
            return False, "No trick selected"

        def _do():
            st = self.high.execute_trick(trick)
            return _status_ok(st), st.message

        return self.run(_do)

    def get_gait(self) -> Tuple[bool, Optional[object], str]:
        if not self.connected:
            return False, None, "Not connected"

        def _do():
            st, g = self.high.get_gait()
            ok = _status_ok(st)
            if ok and _gait_is_sentinel(g) and self._last_gait is not None:
                g = self._last_gait
            elif ok and not _gait_is_sentinel(g):
                self.remember_gait(g)
            return ok, g, st.message

        try:
            return _do()
        except Exception as exc:
            logging.exception("robot command")
            return False, None, str(exc)

    def start_joy_loop(self, get_axes: Callable[[], Tuple[float, float, float, float]]) -> None:
        self._stop_joy()
        self.joy_active = True
        self.joy_thread = threading.Thread(
            target=self._joy_loop, args=(get_axes,), daemon=True
        )
        self.joy_thread.start()

    def _joy_loop(self, get_axes: Callable[[], Tuple[float, float, float, float]]) -> None:
        while self.joy_active and self.connected:
            try:
                lx, ly, rx, ry = get_axes()
                cmd = magicdog.JoystickCommand()
                cmd.left_x_axis = max(-1.0, min(1.0, lx))
                cmd.left_y_axis = max(-1.0, min(1.0, ly))
                cmd.right_x_axis = max(-1.0, min(1.0, rx))
                cmd.right_y_axis = max(-1.0, min(1.0, ry))
                self.high.send_joystick_command(cmd)
            except Exception as exc:
                logging.debug("joystick: %s", exc)
            time.sleep(0.05)

    def _stop_joy(self) -> None:
        self.joy_active = False
        if self.joy_thread:
            self.joy_thread.join(timeout=1.0)
            self.joy_thread = None

    @staticmethod
    def _pick_map_info(map_infos, *, prefer_name: str = "", current_name: str = ""):
        if not map_infos:
            return None
        for key in (prefer_name, current_name):
            if not key:
                continue
            for info in map_infos:
                if info.map_name == key:
                    return info
        return map_infos[0]

    def refresh_maps(self, prefer_map_name: str = "") -> Tuple[bool, str, List[str]]:
        def _do():
            st, info = self.slam.get_all_map_info()
            if not _status_ok(st):
                return False, st.message, []
            names = [m.map_name for m in info.map_infos]
            map_info = self._pick_map_info(
                info.map_infos,
                prefer_name=prefer_map_name,
                current_name=info.current_map_name,
            )
            if map_info:
                self._load_map_raster(map_info)
            elif not info.current_map_name:
                with self._lock:
                    self.current_map_name = ""
            return True, f"maps={len(names)} current={info.current_map_name}", names

        ok, msg, names = False, "", []
        with self._lock:
            if not self.connected:
                return False, "Not connected", []
        try:
            ok, msg, names = _do()
        except Exception as exc:
            ok, msg = False, str(exc)
        return ok, msg, names

    def _load_map_raster(self, map_info) -> None:
        meta = map_info.map_meta_data
        arr = _image_bytes_to_array(meta.map_image_data)
        if arr is None:
            return
        with self._lock:
            self.map_array = arr
            self.map_origin = (
                meta.origin.position[0],
                meta.origin.position[1],
            )
            self.map_resolution = meta.resolution if meta.resolution > 0 else 0.05
            self.current_map_name = map_info.map_name

    def _setup_audio(self) -> str:
        try:
            self.audio = self.robot.get_audio_controller()
            return "Audio: gRPC ready."
        except Exception as exc:
            logging.exception("audio setup")
            self.audio = None
            return f"Audio unavailable ({exc})"

    def _teardown_audio(self) -> None:
        self.audio = None

    def _audio_run(self, fn: Callable[[], Tuple[bool, str]]) -> Tuple[bool, str]:
        if not self.connected:
            return False, "Not connected"
        if not self.audio:
            return False, "Audio controller unavailable"
        try:
            return fn()
        except Exception as exc:
            logging.exception("audio command")
            return False, str(exc)

    def get_volume(self) -> Tuple[bool, Optional[int], str]:
        def _do():
            st, vol = self.audio.get_volume()
            if not _status_ok(st):
                return False, None, st.message
            return True, vol, "ok"

        ok, vol, msg = self._audio_run(_do)
        return ok, vol, msg

    def set_volume(self, volume: int) -> Tuple[bool, str]:
        def _do():
            st = self.audio.set_volume(volume)
            return _status_ok(st), st.message

        return self._audio_run(_do)

    def play_tts(
        self,
        content: str,
        tts_id: str,
        priority,
        mode,
    ) -> Tuple[bool, str]:
        def _do():
            cmd = magicdog.TtsCommand()
            cmd.id = tts_id
            cmd.content = content
            cmd.priority = priority
            cmd.mode = mode
            st = self.audio.play(cmd)
            return _status_ok(st), st.message

        return self._audio_run(_do)

    def stop_tts(self) -> Tuple[bool, str]:
        def _do():
            st = self.audio.stop()
            return _status_ok(st), st.message

        return self._audio_run(_do)

    def get_voice_config_text(self) -> Tuple[bool, str]:
        def _do():
            st, cfg = self.audio.get_voice_config()
            if not _status_ok(st):
                return False, st.message
            sp = cfg.speaker_config.selected
            bot = cfg.bot_config.selected
            dlg = cfg.dialog_config
            wk = cfg.wakeup_config
            lines = [
                f"TTS model: {int(cfg.tts_type)}",
                f"Speaker: {sp.speaker_id} ({sp.region}) speed={cfg.speaker_config.speaker_speed:.2f}",
                f"Bot: {bot.bot_id}",
                f"Wakeup: {wk.name}",
                (
                    f"Dialog: enable={dlg.is_enable} fullduplex={dlg.is_fullduplex_enable} "
                    f"doa={dlg.is_doa_enable} front_doa={dlg.is_front_doa}"
                ),
            ]
            return True, "\n".join(lines)

        return self._audio_run(_do)

    def switch_tts_model(self, tts_type) -> Tuple[bool, str]:
        def _do():
            st = self.audio.switch_tts_voice_model(tts_type)
            return _status_ok(st), st.message

        return self._audio_run(_do)

    def _setup_display(self) -> str:
        try:
            self.display = self.robot.get_display_controller()
            return "Display: gRPC ready."
        except Exception as exc:
            logging.exception("display setup")
            self.display = None
            return f"Display unavailable ({exc})"

    def _teardown_display(self) -> None:
        self.display = None

    def get_all_face_expressions(self) -> Tuple[bool, List[object], str]:
        if not self.connected:
            return False, [], "Not connected"
        if not self.display:
            return False, [], "Display controller unavailable"
        try:
            st, expressions = self.display.get_all_face_expressions()
            if not _status_ok(st):
                return False, [], st.message
            return True, list(expressions), "ok"
        except Exception as exc:
            logging.exception("display command")
            return False, [], str(exc)

    def set_face_expression(self, expression_id: int) -> Tuple[bool, str]:
        if not self.connected:
            return False, "Not connected"
        if not self.display:
            return False, "Display controller unavailable"
        try:
            st = self.display.set_face_expression(int(expression_id))
            return _status_ok(st), st.message
        except Exception as exc:
            logging.exception("display command")
            return False, str(exc)

    def get_current_face_expression(self) -> Tuple[bool, Optional[object], str]:
        if not self.connected:
            return False, None, "Not connected"
        if not self.display:
            return False, None, "Display controller unavailable"
        try:
            st, face = self.display.get_current_face_expression()
            if not _status_ok(st):
                return False, None, st.message
            return True, face, "ok"
        except Exception as exc:
            logging.exception("display command")
            return False, None, str(exc)

    def _setup_sensor(self) -> str:
        try:
            self.sensor = self.robot.get_sensor_controller()
            if not self.sensor.initialize():
                self.sensor = None
                return "Sensor: initialize failed."
            self._sensor_channel_open = False
            for key in self._sensor_hw:
                self._sensor_hw[key] = False
            return "Sensor: gRPC ready."
        except Exception as exc:
            logging.exception("sensor setup")
            self.sensor = None
            return f"Sensor unavailable ({exc})"

    def _teardown_sensor(self) -> None:
        if self.robot:
            for name in ("binocular_camera", "rgbd_camera", "laser_scan"):
                if self._sensor_hw.get(name) and self.sensor:
                    try:
                        if name == "laser_scan":
                            self.sensor.close_laser_scan()
                        elif name == "rgbd_camera":
                            self.sensor.close_rgbd_camera()
                        else:
                            self.sensor.close_binocular_camera()
                    except Exception:
                        logging.exception("sensor close %s", name)
            if self._sensor_channel_open:
                try:
                    self.robot.close_channel_switch()
                except Exception:
                    logging.exception("sensor channel close")
        if self.sensor:
            try:
                self.sensor.shutdown()
            except Exception:
                logging.exception("sensor shutdown")
        self.sensor = None
        self._sensor_channel_open = False
        for key in self._sensor_hw:
            self._sensor_hw[key] = False

    def get_sensor_state(self) -> dict[str, bool]:
        with self._lock:
            return {
                "channel": self._sensor_channel_open,
                **self._sensor_hw,
            }

    def open_sensor_channel(self) -> Tuple[bool, str]:
        if not self.connected or not self.robot:
            return False, "Not connected"
        with self._lock:
            if self._sensor_channel_open:
                return True, "Channel already open"
        try:
            st = self.robot.open_channel_switch()
            ok = _status_ok(st)
            if ok:
                with self._lock:
                    self._sensor_channel_open = True
            return ok, st.message
        except Exception as exc:
            logging.exception("sensor command")
            return False, str(exc)

    def close_sensor_channel(self) -> Tuple[bool, str]:
        if not self.connected or not self.robot:
            return False, "Not connected"
        with self._lock:
            if not self._sensor_channel_open:
                return True, "Channel already closed"
        try:
            st = self.robot.close_channel_switch()
            ok = _status_ok(st)
            if ok:
                with self._lock:
                    self._sensor_channel_open = False
            return ok, st.message
        except Exception as exc:
            logging.exception("sensor command")
            return False, str(exc)

    def open_sensor_hw(self, name: str) -> Tuple[bool, str]:
        if name == "channel":
            return self.open_sensor_channel()
        if name not in self._sensor_hw:
            return False, f"Unknown sensor: {name}"
        if not self.connected:
            return False, "Not connected"
        if not self.sensor:
            return False, "Sensor controller unavailable"
        with self._lock:
            if self._sensor_hw[name]:
                return True, f"{name} already open"
        try:
            if name == "laser_scan":
                st = self.sensor.open_laser_scan()
            elif name == "rgbd_camera":
                st = self.sensor.open_rgbd_camera()
            else:
                st = self.sensor.open_binocular_camera()
            ok = _status_ok(st)
            if ok:
                with self._lock:
                    self._sensor_hw[name] = True
            return ok, st.message
        except Exception as exc:
            logging.exception("sensor command")
            return False, str(exc)

    def close_sensor_hw(self, name: str) -> Tuple[bool, str]:
        if name == "channel":
            return self.close_sensor_channel()
        if name not in self._sensor_hw:
            return False, f"Unknown sensor: {name}"
        if not self.connected:
            return False, "Not connected"
        if not self.sensor:
            return False, "Sensor controller unavailable"
        with self._lock:
            if not self._sensor_hw[name]:
                return True, f"{name} already closed"
        try:
            if name == "laser_scan":
                st = self.sensor.close_laser_scan()
            elif name == "rgbd_camera":
                st = self.sensor.close_rgbd_camera()
            else:
                st = self.sensor.close_binocular_camera()
            ok = _status_ok(st)
            if ok:
                with self._lock:
                    self._sensor_hw[name] = False
            return ok, st.message
        except Exception as exc:
            logging.exception("sensor command")
            return False, str(exc)


@dataclass
class RtspStreamStats:
    """Runtime statistics for an RTSP preview session."""

    fps: float = 0.0
    frame_count: int = 0
    drop_count: int = 0
    source_width: int = 0
    source_height: int = 0
    display_width: int = 0
    display_height: int = 0
    stream_fps_hint: float = 0.0
    elapsed_s: float = 0.0
    _frame_times: List[float] = field(default_factory=list, repr=False)

    def summary(self) -> str:
        src = (
            f"{self.source_width}×{self.source_height}"
            if self.source_width > 0
            else "—"
        )
        disp = (
            f"{self.display_width}×{self.display_height}"
            if self.display_width > 0
            else "—"
        )
        hint = f"{self.stream_fps_hint:.0f}" if self.stream_fps_hint > 0.5 else "—"
        return (
            f"接收 FPS: {self.fps:5.1f}  |  流标注: {hint}  |  "
            f"帧: {self.frame_count}  |  读失败: {self.drop_count}  |  "
            f"源分辨率: {src}  |  显示: {disp}  |  时长: {self.elapsed_s:.0f}s"
        )

    @staticmethod
    def idle_text() -> str:
        return "接收 FPS: —  |  流标注: —  |  帧: —  |  读失败: —  |  源分辨率: —  |  显示: —  |  时长: —"


def _parse_rtsp_url(url: str) -> Tuple[str, int, str]:
    m = re.match(r"rtsp://([^/:]+)(?::(\d+))?(.*)$", url.strip())
    if not m:
        return "", 554, ""
    host = m.group(1)
    port = int(m.group(2) or 554)
    path = (m.group(3) or "").strip()
    return host, port, path


def _build_rtsp_url(host: str, port: int, path: str = "") -> str:
    if path and not path.startswith("/"):
        path = "/" + path
    return f"rtsp://{host}:{port}{path}"


def _rtsp_url_candidates(url: str) -> List[str]:
    host, port, path = _parse_rtsp_url(url)
    if not host:
        return [url.strip()]
    paths: List[str] = []
    if path and path != "/":
        paths.append(path)
    else:
        paths.extend(["", "/stream", "/live", "/h264", "/video", "/cam"])
    seen: set[str] = set()
    out: List[str] = []
    for p in paths:
        candidate = _build_rtsp_url(host, port, p)
        if candidate not in seen:
            seen.add(candidate)
            out.append(candidate)
    return out


def _rtsp_probe_tcp(host: str, port: int, timeout: float = 2.0) -> Tuple[bool, str]:
    if not host:
        return False, "RTSP URL 无效"
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} 端口可达"
    except ConnectionRefusedError:
        return (
            False,
            f"连接被拒绝：{host}:{port} 无服务监听。"
            "请确认机器人已启动相机/RTSP，或修改 URL 端口/路径（如 :8554、/stream）",
        )
    except socket.timeout:
        return False, f"连接超时：{host}:{port}（检查网络与防火墙）"
    except OSError as exc:
        return False, f"无法连接 {host}:{port} — {exc}"


def _open_rtsp_capture(url: str) -> Tuple[Optional[object], str]:
    """Try TCP/UDP and common path suffixes; returns (cap, message)."""
    if not _HAS_RTSP_DEPS:
        return None, "缺少 opencv-python"
    host, port, _path = _parse_rtsp_url(url)
    if host:
        ok, probe_msg = _rtsp_probe_tcp(host, port)
        if not ok:
            return None, probe_msg

    errors: List[str] = []
    for candidate in _rtsp_url_candidates(url):
        for transport in ("tcp", "udp"):
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                f"rtsp_transport;{transport}|stimeout;5000000"
            )
            cap = cv2.VideoCapture(candidate, cv2.CAP_FFMPEG)
            try:
                if cap.isOpened():
                    return cap, f"已连接 {candidate} ({transport})"
            except Exception as exc:
                errors.append(f"{candidate} [{transport}]: {exc}")
            finally:
                if cap is not None and not cap.isOpened():
                    cap.release()
            errors.append(f"{candidate} [{transport}]: open failed")

    detail = errors[0] if len(errors) == 1 else f"已尝试 {len(errors)} 种组合均失败"
    return (
        None,
        f"无法打开 RTSP 流（{detail}）。"
        "请核对 URL，常见示例：rtsp://<IP>:8082/stream",
    )


class RtspPlayer:
    """Background RTSP reader; displays frames on a tk.Label via PIL/ImageTk."""

    _JOIN_TIMEOUT_S = 8.0
    _UI_MIN_INTERVAL_S = 0.05

    def __init__(
        self,
        root: tk.Tk,
        label: tk.Label,
        log_fn: Callable[[str], None],
        max_width: int = 960,
        on_stats: Optional[Callable[[RtspStreamStats], None]] = None,
        on_failed: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.root = root
        self.label = label
        self._log = log_fn
        self._max_width = max_width
        self._on_stats = on_stats
        self._on_failed = on_failed
        self._stats = RtspStreamStats()
        self._stats_lock = threading.Lock()
        self._lifecycle_lock = threading.Lock()
        self._stream_start_mono = 0.0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cap = None
        self._photo = None
        self._url = ""
        self._status = "Stopped"
        self._last_error = ""
        self._last_open_msg = ""

    @property
    def status(self) -> str:
        return self._status

    @property
    def last_error(self) -> str:
        return self._last_error

    @property
    def last_open_msg(self) -> str:
        return self._last_open_msg

    @property
    def is_active(self) -> bool:
        return self._running or (
            self._thread is not None and self._thread.is_alive()
        )

    def get_stats(self) -> RtspStreamStats:
        with self._stats_lock:
            return self._stats

    def _reset_stats(self) -> None:
        with self._stats_lock:
            self._stats = RtspStreamStats()
        self._emit_stats()

    def _emit_stats(self) -> None:
        if self._on_stats:
            self._on_stats(self.get_stats())

    def _record_frame_ok(self, src_w: int, src_h: int, disp_w: int, disp_h: int) -> None:
        now = time.monotonic()
        with self._stats_lock:
            s = self._stats
            s.frame_count += 1
            s.source_width = src_w
            s.source_height = src_h
            s.display_width = disp_w
            s.display_height = disp_h
            if self._stream_start_mono > 0:
                s.elapsed_s = now - self._stream_start_mono
            s._frame_times.append(now)
            window = 1.0
            s._frame_times = [t for t in s._frame_times if t >= now - window]
            if len(s._frame_times) >= 2:
                span = s._frame_times[-1] - s._frame_times[0]
                if span > 0:
                    s.fps = (len(s._frame_times) - 1) / span

    def _record_frame_drop(self) -> None:
        with self._stats_lock:
            self._stats.drop_count += 1

    def _stop_locked(self, wait_s: float = _JOIN_TIMEOUT_S) -> None:
        """Stop capture; VideoCapture is released only inside the capture thread."""
        self._running = False
        thread = self._thread
        self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=wait_s)
        self._cap = None
        self._status = "Stopped"
        self._stream_start_mono = 0.0

    def start(self, url: str) -> bool:
        if not _HAS_RTSP_DEPS:
            self._log("RTSP: install opencv-python and Pillow (see requirements.txt)")
            return False
        url = url.strip()
        if not url:
            self._log("RTSP: URL is empty")
            return False
        with self._lifecycle_lock:
            self._stop_locked()
            self._url = url
            self._last_error = ""
            self._last_open_msg = ""
            self._running = True
            self._stream_start_mono = time.monotonic()
            self._reset_stats()
            self._status = "Connecting…"
            self._thread = threading.Thread(
                target=self._capture_loop, name="rtsp-capture", daemon=True
            )
            self._thread.start()
        self._log(f"RTSP: connecting to {url}")
        return True

    def stop(self) -> None:
        with self._lifecycle_lock:
            self._stop_locked()
        self.root.after(0, self._clear_frame)

    def _clear_frame(self) -> None:
        self._photo = None
        self.label.configure(image="", text="No stream", fg="#94a3b8", bg="#0f172a")
        self._reset_stats()

    def _capture_loop(self) -> None:
        cap = None
        try:
            cap, open_msg = _open_rtsp_capture(self._url)
            with self._lifecycle_lock:
                if not self._running:
                    if cap is not None:
                        try:
                            cap.release()
                        except Exception:
                            pass
                    return
                self._cap = cap
            if cap is None or not cap.isOpened():
                self._status = "Open failed"
                self._last_error = open_msg
                self._log(f"RTSP: cannot open {self._url} — {open_msg}")
                self.root.after(0, self._show_open_failed, open_msg)
                return
            self._last_open_msg = open_msg
            self._log(f"RTSP: {open_msg}")
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            hint_fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
            with self._stats_lock:
                self._stats.stream_fps_hint = hint_fps
            self._status = "Playing"
            fail_streak = 0
            last_ui = 0.0
            while self._running:
                ok, frame = cap.read()
                if not ok or frame is None:
                    fail_streak += 1
                    self._record_frame_drop()
                    if fail_streak > 60:
                        self._status = "Read error"
                        self._log("RTSP: stream read failed")
                        break
                    time.sleep(0.05)
                    continue
                fail_streak = 0
                now = time.monotonic()
                if now - last_ui < self._UI_MIN_INTERVAL_S:
                    continue
                last_ui = now
                try:
                    src_h, src_w = frame.shape[:2]
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    w, h = img.size
                    if w > self._max_width:
                        scale = self._max_width / w
                        img = img.resize(
                            (int(w * scale), int(h * scale)), Image.Resampling.LANCZOS
                        )
                    disp_w, disp_h = img.size
                    photo = ImageTk.PhotoImage(image=img)
                    self._record_frame_ok(src_w, src_h, disp_w, disp_h)
                    self.root.after(0, self._show_frame, photo)
                except Exception as exc:
                    logging.debug("RTSP frame: %s", exc)
        except Exception as exc:
            logging.exception("RTSP capture loop")
            self._status = "Read error"
            self._log(f"RTSP: capture error — {exc}")
        finally:
            self._running = False
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass
            with self._lifecycle_lock:
                if self._cap is cap:
                    self._cap = None

    def _show_frame(self, photo: ImageTk.PhotoImage) -> None:
        if self._status != "Playing":
            return
        self._photo = photo
        self.label.configure(image=photo, text="")

    def _show_open_failed(self, message: str) -> None:
        self._photo = None
        short = message if len(message) <= 200 else message[:197] + "…"
        self.label.configure(
            image="",
            text=f"RTSP 连接失败\n{short}",
            fg="#fca5a5",
            bg="#0f172a",
            wraplength=520,
            justify=tk.CENTER,
        )
        if self._on_failed:
            self._on_failed(message)


def _robot_host_from_addr(addr: str) -> str:
    addr = addr.strip()
    if not addr:
        return "192.168.55.200"
    if addr.startswith("rtsp://"):
        m = re.match(r"rtsp://([^/:]+)", addr)
        return m.group(1) if m else addr
    return addr.split(":", 1)[0]


class NavVizApp:
    def __init__(
        self,
        default_local_ip: str,
        default_robot_ip: str,
        rtsp_port: int = 8082,
        rtsp_path: str = "",
    ) -> None:
        self.rtsp_port = rtsp_port
        self.rtsp_path = rtsp_path.strip()
        self._rtsp_start_pending_log = False
        self.default_robot_ip = default_robot_ip
        self.session = RobotSession()
        self.root = tk.Tk()
        self.root.title("MagicDog · Nav Viz")
        self.root.geometry("1160x780")
        self.root.minsize(880, 560)
        self.theme = AppTheme(self.root)
        self.theme.apply()

        outer = ttk.Frame(self.root)
        outer.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.theme.PAD_OUTER,
            pady=self.theme.PAD_OUTER,
        )

        self._build_header(outer)
        self._build_connection_bar(outer, default_local_ip, default_robot_ip)

        self._main_paned = tk.PanedWindow(outer, orient=tk.VERTICAL)
        self.theme.paned_config(self._main_paned)
        self._main_paned.pack(fill=tk.BOTH, expand=True, pady=(self.theme.PAD_TAB, 0))

        tab_host = ttk.Frame(self._main_paned)
        self._main_paned.add(tab_host, minsize=280)

        nb_shell = tk.Frame(
            tab_host,
            bg=self.theme.BORDER,
            highlightbackground=self.theme.BORDER,
            highlightthickness=1,
        )
        nb_shell.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        nb_inner = tk.Frame(nb_shell, bg=self.theme.SURFACE)
        nb_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.notebook = ttk.Notebook(nb_inner)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 0))

        self._map_goal_pose: Optional[Tuple[float, float, float]] = None
        self._map_init_pose: Optional[Tuple[float, float, float]] = None
        self._map_rotate: Optional[dict] = None
        self._joy_axes_source = "motion"

        self._build_motion_tab()
        self._build_slam_tab()
        self._build_nav_map_tab()
        self._build_audio_tab()
        self._build_display_tab()
        self._build_sensor_tab()
        self._build_video_tab()

        log_host = ttk.Frame(self._main_paned)
        self._main_paned.add(log_host, minsize=96)
        self._build_log_panel(log_host)

        self.root.after(100, self._init_main_paned_sash)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._schedule_map_redraw()

    def _build_header(self, parent: ttk.Frame) -> None:
        t = self.theme
        shell = tk.Frame(parent, bg=t.BORDER, highlightthickness=0)
        shell.pack(fill=tk.X, pady=(0, t.PAD_TAB))
        card = tk.Frame(shell, bg=t.SURFACE)
        card.pack(fill=tk.X, padx=1, pady=1)
        bar = tk.Frame(card, bg=t.HEADER_BAR, height=3)
        bar.pack(fill=tk.X)
        row = tk.Frame(card, bg=t.SURFACE)
        row.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        brand = tk.Frame(row, bg=t.SURFACE)
        brand.pack(side=tk.LEFT)
        tk.Label(
            brand,
            text="MagicDog",
            bg=t.SURFACE,
            fg=t.ACCENT,
            font=t.font_title,
        ).pack(side=tk.LEFT)
        tk.Label(
            brand,
            text=" Nav Viz",
            bg=t.SURFACE,
            fg=t.TEXT,
            font=t.font_title,
        ).pack(side=tk.LEFT)
        tk.Label(
            row,
            text="gRPC  ·  Motion  ·  SLAM  ·  Nav  ·  Audio  ·  Display  ·  Sensor  ·  Video",
            bg=t.SURFACE,
            fg=t.TEXT_HINT,
            font=t.font_subtitle,
        ).pack(side=tk.LEFT, padx=(14, 0))
        tk.Label(
            row,
            text="SDK GUI",
            bg=t.SURFACE,
            fg=t.TEXT_HINT,
            font=t.font_subtitle,
        ).pack(side=tk.RIGHT)

    def _log(self, msg: str) -> None:
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        logging.info(msg)

    def _clear_action_feedback(self) -> None:
        if not hasattr(self, "action_pill"):
            return
        self.action_pill.config(text=" IDLE ", bg=self.theme.PILL_IDLE, fg="#f8fafc")
        self.action_feedback.config(text="等待操作…", style="StatusIdle.TLabel")

    def _show_action_feedback(
        self, action: str, ok: Optional[bool], detail: str = ""
    ) -> None:
        if not hasattr(self, "action_pill"):
            return
        detail = (detail or "").strip()
        if len(detail) > 100:
            detail = detail[:97] + "..."
        if ok is None:
            pill, style, bg = " ··· ", "StatusWarn.TLabel", self.theme.WARN
            headline = f"{action} — 执行中…"
        elif ok:
            pill, style, bg = " OK ", "StatusOk.TLabel", self.theme.SUCCESS
            headline = f"{action} — 成功"
        else:
            pill, style, bg = " FAIL ", "StatusBad.TLabel", self.theme.DANGER
            headline = f"{action} — 失败"
        text = f"{headline}  {detail}" if detail else headline
        pill_fg = "#0f172a" if ok is None else "#f8fafc"
        self.action_pill.config(text=pill, bg=bg, fg=pill_fg)
        self.action_feedback.config(text=text, style=style)
        aid = getattr(self, "_action_feedback_after_id", None)
        if aid:
            self.root.after_cancel(aid)
        self._action_feedback_after_id = self.root.after(10000, self._clear_action_feedback)

    def _action_busy(self, action: str, detail: str = "执行中…") -> None:
        self._show_action_feedback(action, None, detail)
        self.root.update_idletasks()

    def _log_action(self, action: str, ok: bool, detail: str) -> None:
        self._log(f"{action}: {detail}" if ok else f"{action} FAILED: {detail}")
        self._show_action_feedback(action, ok, detail)

    def _wrap_action(self, action: str, cmd: Callable[[], None]) -> Callable[[], None]:
        def wrapped() -> None:
            self._action_busy(action)
            try:
                cmd()
            except Exception as exc:
                logging.exception(action)
                self._log_action(action, False, str(exc))

        return wrapped

    def _build_connection_bar(self, parent: ttk.Frame, local_ip: str, robot_ip: str) -> None:
        t = self.theme
        card = ttk.LabelFrame(parent, text=" Connection ")
        card.pack(fill=tk.X, pady=t.PAD_ROW)
        inner = ttk.Frame(card, style="Card.TFrame")
        inner.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)

        row = ttk.Frame(inner, style="Card.TFrame")
        row.pack(fill=tk.X)
        ttk.Label(row, text="Local IP", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.local_ip_var = tk.StringVar(value=local_ip)
        ttk.Entry(row, textvariable=self.local_ip_var, width=16).pack(side=tk.LEFT, padx=(6, 16))
        ttk.Label(row, text="Robot gRPC", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.robot_ip_var = tk.StringVar(value=robot_ip)
        ttk.Entry(row, textvariable=self.robot_ip_var, width=16).pack(side=tk.LEFT, padx=(6, 16))
        ttk.Button(
            row,
            text="Connect",
            style="Accent.TButton",
            command=self._wrap_action("Connect", self._on_connect),
        ).pack(side=tk.LEFT, padx=(4, 6))
        ttk.Button(
            row,
            text="Disconnect",
            style="Muted.TButton",
            command=self._wrap_action("Disconnect", self._on_disconnect),
        ).pack(side=tk.LEFT, padx=4)

        status_panel = t.inset_panel(inner, pady=(t.PAD_ROW, 0), padx=0, bg=t.SURFACE)
        status_row = ttk.Frame(status_panel, style="Card.TFrame")
        status_row.pack(fill=tk.X, padx=t.PAD_ROW, pady=t.PAD_ROW)
        self._conn_dot = tk.Label(
            status_row,
            text="●",
            bg=t.SURFACE,
            fg=t.PILL_IDLE,
            font=t.font_ui_bold,
        )
        self._conn_dot.pack(side=tk.LEFT)
        self.conn_label = ttk.Label(
            status_row, text="Disconnected", style="StatusIdle.TLabel"
        )
        self.conn_label.pack(side=tk.LEFT, padx=(2, 0))
        ttk.Label(
            status_row,
            text="GrpcOnly · HIGH_LEVEL_MOTION | SLAM_NAVIGATION",
            style="CardMuted.TLabel",
        ).pack(side=tk.RIGHT)

    def _init_main_paned_sash(self) -> None:
        """Keep Log pane visible (~140px tall); user can drag the sash above it."""
        if not hasattr(self, "_main_paned"):
            return
        try:
            h = self._main_paned.winfo_height()
            if h > 180:
                self._main_paned.sashpos(0, max(280, h - 112))
        except tk.TclError:
            pass

    def _build_log_panel(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        lf = ttk.LabelFrame(parent, text=" Log · 操作反馈 ")
        lf.pack(fill=tk.BOTH, expand=True)
        fb_panel = self.theme.inset_panel(lf, pady=(self.theme.PAD_ROW, 2), padx=0)
        fb_row = ttk.Frame(fb_panel, style="Card.TFrame")
        fb_row.pack(fill=tk.X, padx=self.theme.PAD_ROW, pady=self.theme.PAD_ROW)
        self.action_pill = self.theme.make_pill(
            fb_row, " IDLE ", bg=self.theme.PILL_IDLE
        )
        self.action_pill.pack(side=tk.LEFT)
        self.action_feedback = ttk.Label(
            fb_row,
            text="等待操作…",
            style="StatusIdle.TLabel",
            wraplength=960,
        )
        self.action_feedback.pack(side=tk.LEFT, padx=(6, 0), fill=tk.X, expand=True)
        self._action_feedback_after_id: Optional[str] = None

        log_wrap = tk.Frame(
            lf,
            bg=self.theme.LOG_BORDER,
            highlightthickness=0,
        )
        log_wrap.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.theme.PAD_INNER,
            pady=(0, self.theme.PAD_INNER),
        )
        log_body = self.theme.scroll_body(log_wrap, border=False)
        self.log_box = tk.Text(
            log_body,
            height=self.theme.LOG_LINES,
            state=tk.NORMAL,
            font=self.theme.font_mono,
            bg=self.theme.LOG_BG,
            fg=self.theme.LOG_FG,
            insertbackground=self.theme.LOG_FG,
            relief=tk.FLAT,
            padx=8,
            pady=6,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
        )
        self.log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.theme.mount_scroll_rail(log_body, self.log_box)
        bind_content_drag_scroll(self.log_box)

    def _build_motion_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Motion ")
        tab.columnconfigure(0, weight=1)

        t = self.theme
        gf = ttk.LabelFrame(tab, text=" Gait ")
        gf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=(t.PAD_TAB, t.PAD_ROW))
        gait_row = ttk.Frame(gf, style="Card.TFrame")
        gait_row.pack(fill=tk.X, padx=t.PAD_ROW, pady=(t.PAD_ROW, t.PAD_ROW))
        self.gait_var = tk.StringVar(value=GAIT_CHOICES[0][0])
        gait_cb = ttk.Combobox(
            gait_row,
            textvariable=self.gait_var,
            values=[n for n, _, _ in GAIT_CHOICES],
            state="readonly",
            width=42,
        )
        gait_cb.pack(side=tk.LEFT, padx=(0, 8))
        gait_cb.bind("<<ComboboxSelected>>", self._on_gait_selected)
        ttk.Button(
            gait_row,
            text="Set gait",
            style="Accent.TButton",
            command=self._wrap_action("Set gait", self._on_set_gait),
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            gait_row,
            text="Get gait",
            command=self._wrap_action("Get gait", self._on_get_gait),
        ).pack(side=tk.LEFT, padx=4)
        gait_status_row = ttk.Frame(gf, style="Card.TFrame")
        gait_status_row.pack(fill=tk.X, padx=t.PAD_ROW, pady=(0, t.PAD_ROW))
        self.gait_current_label = ttk.Label(
            gait_status_row,
            text="当前步态：— （未连接）",
            style="StatusIdle.TLabel",
            wraplength=t.INFO_WRAP,
        )
        self.gait_current_label.pack(anchor=tk.W)
        self.gait_desc_label = self.theme.info_box(
            gf, _choice_desc(GAIT_CHOICES, GAIT_CHOICES[0][0])
        )
        self.gait_var.trace_add("write", self._on_gait_selected)

        tf = ttk.LabelFrame(tab, text=" Trick ")
        tf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        trick_row = ttk.Frame(tf, style="Card.TFrame")
        trick_row.pack(fill=tk.X, padx=t.PAD_ROW, pady=(t.PAD_ROW, t.PAD_ROW))
        self.trick_var = tk.StringVar(value=TRICK_CHOICES[0][0])
        trick_cb = ttk.Combobox(
            trick_row,
            textvariable=self.trick_var,
            values=[n for n, _, _ in TRICK_CHOICES],
            state="readonly",
            width=38,
        )
        trick_cb.pack(side=tk.LEFT, padx=(0, 8))
        trick_cb.bind("<<ComboboxSelected>>", self._on_trick_selected)
        ttk.Button(
            trick_row,
            text="Execute",
            style="Accent.TButton",
            command=self._wrap_action("Execute trick", self._on_trick),
        ).pack(side=tk.LEFT, padx=4)
        self.trick_desc_label = self.theme.info_box(
            tf, _choice_desc(TRICK_CHOICES, TRICK_CHOICES[0][0])
        )
        self.trick_var.trace_add("write", self._on_trick_selected)

        self._joy_frame = ttk.LabelFrame(tab, text=" Virtual joysticks · 20 Hz ")
        self._joy_frame.pack(fill=tk.X, padx=t.PAD_FRAME, pady=(t.PAD_ROW, t.PAD_TAB))

        joy_row = ttk.Frame(self._joy_frame, style="Card.TFrame")
        joy_row.pack(fill=tk.X, padx=t.PAD_ROW, pady=t.PAD_ROW)

        self.joy_sticks_border = tk.Frame(
            joy_row,
            bg=self.theme.SURFACE_ALT,
            highlightthickness=2,
            highlightbackground=self.theme.BORDER,
        )
        self.joy_sticks_border.pack(side=tk.LEFT, padx=(0, t.PAD_INNER))

        sticks = ttk.Frame(self.joy_sticks_border)
        sticks.pack(pady=t.PAD_ROW)

        js = t.JOY_SIZE
        self.left_stick = VirtualJoystick(
            sticks, size=js, label="Left\nX lateral · Y fwd"
        )
        self.left_stick.pack(side=tk.LEFT, padx=12)

        self.right_stick = VirtualJoystick(
            sticks,
            size=js,
            label="Right\nX yaw",
            horizontal_only=True,
        )
        self.right_stick.pack(side=tk.LEFT, padx=12)

        state_card = ttk.LabelFrame(joy_row, text=" RobotState ")
        state_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        state_inner = tk.Frame(state_card, bg=self.theme.SURFACE_ALT)
        state_inner.pack(fill=tk.BOTH, expand=True, padx=t.PAD_ROW, pady=t.PAD_ROW)
        self.motion_robot_state_text = tk.Text(
            state_inner,
            height=9,
            width=38,
            font=self.theme.font_mono,
            bg=self.theme.SURFACE_ALT,
            fg=self.theme.TEXT,
            relief=tk.FLAT,
            highlightthickness=0,
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=6,
            pady=4,
        )
        self.motion_robot_state_text.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1
        )
        self.theme.mount_scroll_rail(state_inner, self.motion_robot_state_text)
        bind_content_drag_scroll(
            state_inner, target=self.motion_robot_state_text
        )
        self._set_motion_robot_state_text(
            _format_motion_robot_state(False, None, None)
        )

        bf = ttk.Frame(self._joy_frame, style="Card.TFrame")
        bf.pack(fill=tk.X, pady=t.PAD_ROW, padx=t.PAD_ROW)
        self.joy_start_btn = ttk.Button(
            bf,
            text="▶  Start stream",
            style="Accent.TButton",
            command=self._wrap_action(
                "Start stream", lambda: self._on_joy_start("motion")
            ),
        )
        self.joy_start_btn.pack(side=tk.LEFT, padx=6)
        self.joy_stop_btn = ttk.Button(
            bf,
            text="■  Stop",
            style="Muted.TButton",
            command=self._wrap_action("Stop stream", self._on_joy_stop),
            state=tk.DISABLED,
        )
        self.joy_stop_btn.pack(side=tk.LEFT, padx=6)
        self.joy_status_pill = self.theme.make_pill(
            bf, "  已停止  ", bg=self.theme.PILL_IDLE
        )
        self.joy_status_pill.pack(side=tk.LEFT, padx=8)
        self.joy_status_label = ttk.Label(bf, text="未向机器人发送摇杆指令", style="CardMuted.TLabel")
        self.joy_status_label.pack(side=tk.LEFT, padx=4)

        ttk.Label(
            self._joy_frame,
            text="推流：按住移动，松开回零；Stop 结束。",
            style="CardHint.TLabel",
        ).pack(pady=(0, t.PAD_ROW))
        self._update_joy_stream_ui(False)

    def _scrollable_frame(self, parent: tk.Widget) -> ttk.Frame:
        """Return an inner frame; pack all tab content into it for vertical drag scrolling."""
        t = self.theme
        shell = tk.Frame(
            parent,
            bg=t.BORDER,
            highlightbackground=t.BORDER,
            highlightthickness=1,
        )
        shell.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        body = tk.Frame(shell, bg=t.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        viewport = tk.Frame(body, bg=t.SURFACE_ALT)
        viewport.pack(fill=tk.BOTH, expand=True, padx=t.PAD_ROW, pady=t.PAD_ROW)

        canvas = tk.Canvas(
            viewport,
            highlightthickness=0,
            bg=t.SURFACE,
            borderwidth=0,
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0), pady=2)
        t.mount_scroll_rail(viewport, canvas)
        bind_content_drag_scroll(canvas)

        inner = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def _on_inner_configure(_event=None) -> None:
            y0 = canvas.yview()[0]
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(y0)

        def _on_canvas_configure(event) -> None:
            canvas.itemconfigure(win_id, width=event.width)

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        return inner

    def _slam_flow_arrow(self, parent: ttk.Frame, text: str) -> None:
        t = self.theme
        wrap = t.inset_panel(parent, pady=t.PAD_ROW, padx=t.PAD_ROW)
        ttk.Label(wrap, text=text, style="FlowHint.TLabel").pack(
            anchor=tk.CENTER, pady=t.PAD_ROW
        )

    def _slam_step(
        self,
        parent: ttk.Frame,
        badge: str,
        title: str,
        detail: str,
        actions: Optional[List[Tuple[str, Callable[[], None], bool]]] = None,
        extra_widget: Optional[Callable[[ttk.Frame], None]] = None,
    ) -> None:
        t = self.theme
        shell = tk.Frame(parent, bg=t.BORDER, highlightthickness=0)
        shell.pack(fill=tk.X, padx=t.PAD_ROW, pady=t.PAD_ROW)
        tk.Frame(shell, bg=t.ACCENT, width=3).pack(side=tk.LEFT, fill=tk.Y)
        row = ttk.Frame(shell, style="Card.TFrame")
        row.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        row.columnconfigure(1, weight=1)

        badge_lbl = tk.Label(
            row,
            text=badge,
            bg=t.ACCENT,
            fg="#ffffff",
            font=t.font_ui_bold,
            padx=5,
            pady=2,
        )
        badge_lbl.grid(row=0, column=0, rowspan=2, padx=(t.PAD_ROW, 6), sticky=tk.N)
        ttk.Label(row, text=title, style="StepTitle.TLabel").grid(row=0, column=1, sticky=tk.W)
        ttk.Label(row, text=detail, style="StepDetail.TLabel", wraplength=420).grid(
            row=1, column=1, sticky=tk.W, pady=(0, 0)
        )

        if actions or extra_widget:
            act = ttk.Frame(row, style="Card.TFrame")
            act.grid(row=0, column=2, rowspan=2, padx=(8, 0), sticky=tk.E)
            if extra_widget:
                extra_widget(act)
            for label, cmd, accent in actions or []:
                style = "Accent.TButton" if accent else "TButton"
                ttk.Button(
                    act,
                    text=label,
                    style=style,
                    command=self._wrap_action(label, cmd),
                ).pack(side=tk.LEFT if extra_widget else tk.TOP, padx=3, pady=1)

    def _build_slam_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" SLAM ")
        scroll = self._scrollable_frame(tab)

        self.theme.info_box(
            scroll,
            "推荐顺序：流程 A 建新图 → 流程 B 加载并定位 → Navigation 页设初始位姿并开启导航。"
            "建图/导航前请在 Motion 页将步态切为 Down climb stairs。"
            "定位完成后到 Navigation & Map 页继续。",
        )

        t = self.theme
        phase_a = ttk.LabelFrame(scroll, text=" 流程 A · 建图 ")
        phase_a.pack(fill=tk.X, padx=t.PAD_FRAME, pady=(t.PAD_ROW, t.PAD_ROW))

        self._slam_step(
            phase_a,
            "①",
            "开始建图",
            "进入 SLAM 建图模式；取消则放弃本次建图。",
            [
                ("开始建图", self._on_start_mapping, True),
                ("取消建图", self._on_cancel_mapping, False),
            ],
        )
        self._slam_step(
            phase_a,
            "②",
            "驱动机器人探索",
            "切换到 Motion 页，Start stream 后用虚拟摇杆巡逻；覆盖需建图区域。",
            None,
        )

        self.save_map_name = tk.StringVar(value="map_gui")

        def _save_row(act_frame: ttk.Frame) -> None:
            ttk.Label(act_frame, text="地图名", style="CardMuted.TLabel").pack(side=tk.LEFT)
            ttk.Entry(act_frame, textvariable=self.save_map_name, width=18).pack(
                side=tk.LEFT, padx=6
            )

        self._slam_step(
            phase_a,
            "③",
            "保存地图",
            "建图结束后填写名称并保存；保存后执行流程 B，再到 Navigation & Map 页查看。",
            [("保存地图", self._on_save_map, True)],
            extra_widget=_save_row,
        )

        self._slam_flow_arrow(scroll, "— 已有地图可跳过流程 A，从流程 B 开始 —")

        phase_b = ttk.LabelFrame(scroll, text=" 流程 B · 加载地图并定位 ")
        phase_b.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)

        self._slam_step(
            phase_b,
            "④",
            "刷新地图列表",
            "从机器人读取已保存地图；保存新图后建议先刷新再加载。",
            [("刷新列表", self._on_refresh_maps, True)],
        )

        list_panel, self.map_list = self.theme.listbox_panel(phase_b, height=4)
        list_panel.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_ROW)

        self._slam_step(
            phase_b,
            "⑤",
            "加载选中地图",
            "在列表中选中一张地图，加载为当前 SLAM 地图。",
            [("加载选中", self._on_load_map, True)],
        )
        self._slam_step(
            phase_b,
            "⑥",
            "切换定位模式",
            "进入定位；随后到 Navigation & Map 页按流程 C 操作。",
            [("切换定位", self._on_switch_loc, True)],
        )

        self._slam_flow_arrow(scroll, "— 继续在 Navigation & Map 页完成导航 —")

        util = ttk.LabelFrame(scroll, text=" 维护 ")
        util.pack(fill=tk.X, padx=t.PAD_FRAME, pady=(t.PAD_ROW, t.PAD_TAB))
        util_row = ttk.Frame(util, style="Card.TFrame")
        util_row.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        util_btns = ttk.Frame(util_row, style="Card.TFrame")
        util_btns.pack(fill=tk.X)
        ttk.Button(
            util_btns,
            text="删除选中地图",
            command=self._wrap_action("删除选中地图", self._on_delete_map),
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            util_btns,
            text="关闭 SLAM（Idle）",
            command=self._wrap_action("关闭 SLAM", self._on_slam_idle),
        ).pack(side=tk.LEFT, padx=4)
        ttk.Label(
            util_row,
            text="结束 SLAM/导航会话时建议点 Idle。",
            style="CardMuted.TLabel",
            wraplength=t.INFO_WRAP,
        ).pack(anchor=tk.W, padx=4, pady=(t.PAD_ROW, 0))

    def _build_map_symbol_legend(self, parent: tk.Widget) -> None:
        t = self.theme
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(side=tk.LEFT, padx=(8, 0))

        def _legend_item(kind: str, fg: str, arrow_fg: str, caption: str) -> None:
            cell = ttk.Frame(row, style="Card.TFrame")
            cell.pack(side=tk.LEFT, padx=(0, 10))
            icon = tk.Canvas(
                cell, width=26, height=14, highlightthickness=0, bg=t.SURFACE_ALT
            )
            icon.pack(side=tk.LEFT)
            _paint_map_legend_icon(icon, kind, fg, arrow_fg)
            ttk.Label(cell, text=caption, style="CardMuted.TLabel").pack(
                side=tk.LEFT, padx=(3, 0)
            )

        _legend_item("robot", "#34d399", "#34d399", "绿·定位")
        _legend_item("init", "#fbbf24", "#fbbf24", "黄·初姿")
        _legend_item("goal", "#f87171", "#fca5a5", "红·目标")

    def _build_nav_map_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Nav ")

        self.init_pose_x = tk.DoubleVar(value=0.0)
        self.init_pose_y = tk.DoubleVar(value=0.0)
        self.init_pose_yaw = tk.DoubleVar(value=0.0)
        self.init_pose_roll = tk.DoubleVar(value=0.0)
        self.init_pose_pitch = tk.DoubleVar(value=0.0)
        self.goal_pose_x = tk.DoubleVar(value=0.0)
        self.goal_pose_y = tk.DoubleVar(value=0.0)
        self.goal_pose_yaw = tk.DoubleVar(value=0.0)
        self.map_click_mode = tk.StringVar(value="goal")

        t = self.theme
        paned = tk.PanedWindow(tab, orient=tk.HORIZONTAL)
        self.theme.paned_config(paned)
        paned.pack(fill=tk.BOTH, expand=True, padx=t.PAD_INNER, pady=t.PAD_INNER)

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, minsize=260)
        paned.add(right, minsize=380)

        left_scroll = self._scrollable_frame(left)

        self.theme.info_box(
            left_scroll,
            "流程 C：⑦刷新地图 → ⑧开导航 → ⑨初姿 → ⑩目标导航。"
            "地图左键设点、右键拖朝向、双击提交。",
            wraplength=300,
        )

        phase_c = ttk.LabelFrame(left_scroll, text=" 流程 C · 地图导航 ")
        phase_c.pack(fill=tk.X, padx=t.PAD_ROW, pady=t.PAD_ROW)

        self._slam_step(
            phase_c,
            "⑦",
            "刷新地图显示",
            "从机器人拉取当前地图栅格；需先在 SLAM 页加载地图。",
            [("刷新地图", self._on_refresh_maps, True)],
        )
        self._slam_step(
            phase_c,
            "⑧",
            "开启导航模式",
            "激活 Grid Map 导航；定位未成功时可能失败。",
            [("Nav mode ON", self._on_nav_on, True)],
        )
        self._slam_step(
            phase_c,
            "⑨",
            "设置初始位姿",
            "填写位置与姿态(Roll/Pitch/Yaw)；地图左键设位置、右键按住旋转设朝向；左键双击提交。",
            [
                ("提交 Init pose", self._on_init_pose, True),
                ("填入定位位姿", self._on_copy_init_pose, False),
            ],
        )

        pose_card = ttk.LabelFrame(phase_c, text=" 位姿参数 ")
        pose_card.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_ROW)
        inner = ttk.Frame(pose_card, style="Card.TFrame")
        inner.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        ttk.Label(inner, text="初始位姿", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, pady=2)
        init_fields = [
            ("X", self.init_pose_x),
            ("Y", self.init_pose_y),
            ("Yaw", self.init_pose_yaw),
            ("Roll", self.init_pose_roll),
            ("Pitch", self.init_pose_pitch),
        ]
        for i, (lbl, var) in enumerate(init_fields):
            ttk.Label(inner, text=f"{lbl}", style="CardMuted.TLabel").grid(
                row=0, column=1 + i * 2, padx=(8, 2), sticky=tk.E
            )
            ttk.Entry(inner, textvariable=var, width=8).grid(row=0, column=2 + i * 2, padx=2)
        ttk.Label(inner, text="(rad)", style="CardMuted.TLabel").grid(row=0, column=11, padx=2)

        ttk.Label(inner, text="导航目标", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, pady=(4, 2))
        for i, (lbl, var) in enumerate(
            [("X", self.goal_pose_x), ("Y", self.goal_pose_y), ("Yaw", self.goal_pose_yaw)]
        ):
            ttk.Label(inner, text=f"{lbl}", style="CardMuted.TLabel").grid(
                row=1, column=1 + i * 2, padx=(8, 2), sticky=tk.E
            )
            ttk.Entry(inner, textvariable=var, width=8).grid(row=1, column=2 + i * 2, padx=2)
        ttk.Label(inner, text="(rad)", style="CardMuted.TLabel").grid(row=1, column=7, padx=2)
        ttk.Button(
            inner,
            text="目标 Yaw ← 定位",
            command=self._wrap_action("目标 Yaw ← 定位", self._on_copy_goal_yaw),
        ).grid(row=1, column=8, columnspan=3, padx=8, sticky=tk.W)

        self._slam_step(
            phase_c,
            "⑩",
            "地图选点并导航",
            "选「导航目标」后单击设点；点「导航到目标点」或双击地图发起任务。",
            [
                ("导航到目标点", self._on_set_goal, True),
                ("暂停", self._on_nav_pause, False),
                ("继续", self._on_nav_resume, False),
                ("取消任务", self._on_nav_cancel, False),
            ],
        )
        ttk.Button(
            phase_c,
            text="查询导航状态",
            command=self._wrap_action("查询导航状态", self._on_nav_status),
        ).pack(anchor=tk.W, padx=t.PAD_INNER, pady=(0, t.PAD_ROW))

        status = ttk.LabelFrame(left_scroll, text=" 实时状态 ")
        status.pack(fill=tk.X, padx=t.PAD_ROW, pady=t.PAD_ROW)
        st_inner = ttk.Frame(status, style="Card.TFrame")
        st_inner.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        self.loc_label = ttk.Label(st_inner, text="Localization: —", style="Card.TLabel")
        self.loc_label.pack(anchor=tk.W, pady=2)
        self.nav_label = ttk.Label(st_inner, text="Nav: —", style="CardMuted.TLabel")
        self.nav_label.pack(anchor=tk.W, pady=2)

        plot_card = ttk.LabelFrame(right, text=" 占用栅格地图 ")
        plot_card.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        map_toolbar = ttk.Frame(plot_card, style="Card.TFrame")
        map_toolbar.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        ttk.Label(map_toolbar, text="地图点击", style="CardMuted.TLabel").pack(side=tk.LEFT)
        ttk.Radiobutton(
            map_toolbar,
            text="导航目标",
            variable=self.map_click_mode,
            value="goal",
            command=self._on_map_click_mode_changed,
        ).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(
            map_toolbar,
            text="初始位姿",
            variable=self.map_click_mode,
            value="init",
            command=self._on_map_click_mode_changed,
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            map_toolbar,
            text="导航到目标点",
            style="Accent.TButton",
            command=self._wrap_action("导航到目标点", self._on_set_goal),
        ).pack(side=tk.RIGHT, padx=4)
        ttk.Button(
            map_toolbar,
            text="提交 Init pose",
            command=self._wrap_action("提交 Init pose", self._on_init_pose),
        ).pack(side=tk.RIGHT, padx=4)

        map_info_panel = t.inset_panel(plot_card, pady=(0, t.PAD_ROW), padx=0)
        map_info_row = ttk.Frame(map_info_panel, style="Card.TFrame")
        map_info_row.pack(fill=tk.X, padx=t.PAD_ROW, pady=t.PAD_ROW)
        self.map_meta_label = ttk.Label(
            map_info_row,
            text="origin: —  ·  resolution: —  ·  size: —",
            style="StatusIdle.TLabel",
        )
        self.map_meta_label.pack(side=tk.LEFT, anchor=tk.W)
        self._build_map_symbol_legend(map_info_row)

        map_plot_shell = tk.Frame(plot_card, bg=t.BORDER)
        map_plot_shell.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        map_plot_inner = tk.Frame(map_plot_shell, bg=self.theme.MAP_BG)
        map_plot_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.fig = Figure(figsize=(4.9, 4.3), dpi=96, facecolor=self.theme.MAP_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.theme.MAP_BG)
        self.ax.tick_params(colors="#94a3b8", labelsize=self.theme.SZ_MAP_TICK)
        for spine in self.ax.spines.values():
            spine.set_color("#475569")
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_plot_inner)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.canvas.mpl_connect("button_press_event", self._on_map_press)
        self.canvas.mpl_connect("motion_notify_event", self._on_map_motion)
        self.canvas.mpl_connect("button_release_event", self._on_map_release)
        map_widget = self.canvas.get_tk_widget()
        map_widget.bind("<Button-3>", lambda _e: "break")  # suppress Tk context menu on map

        ttk.Label(
            plot_card,
            text="左键=位置  ·  右键按住拖动=旋转朝向  ·  左键双击=提交",
            style="CardHint.TLabel",
        ).pack(pady=(0, t.PAD_ROW))

    def _set_motion_robot_state_text(self, text: str) -> None:
        if not hasattr(self, "motion_robot_state_text"):
            return
        if text == getattr(self, "_motion_robot_state_cached", None):
            return
        w = self.motion_robot_state_text
        y0 = w.yview()[0]
        w.config(state=tk.NORMAL)
        w.delete("1.0", tk.END)
        w.insert("1.0", text)
        w.config(state=tk.DISABLED)
        w.yview_moveto(y0)
        self._motion_robot_state_cached = text

    def _update_motion_robot_state_panel(self) -> None:
        if not hasattr(self, "motion_robot_state_text"):
            return
        with self.session._lock:
            connected = self.session.connected
            state = self.session.robot_state
            loc = self.session.localization
        self._set_motion_robot_state_text(
            _format_motion_robot_state(connected, state, loc)
        )

    def _schedule_map_redraw(self) -> None:
        self._redraw_map()
        self._update_status_labels()
        self._update_motion_robot_state_panel()
        self.root.after(500, self._schedule_map_redraw)

    def _update_map_meta_label(
        self,
        arr: Optional[np.ndarray],
        origin: Tuple[float, float],
        res: float,
    ) -> None:
        if not hasattr(self, "map_meta_label"):
            return
        if arr is None:
            self.map_meta_label.config(
                text="origin: —  ·  resolution: —  ·  size: —",
                style="StatusIdle.TLabel",
            )
            return
        h, w = arr.shape
        self.map_meta_label.config(
            text=(
                f"origin: ({origin[0]:.3f}, {origin[1]:.3f}) m  ·  "
                f"resolution: {res:.4f} m/px  ·  "
                f"size: {w}×{h} px"
            ),
            style="CardMuted.TLabel",
        )

    def _redraw_map(self) -> None:
        with self.session._lock:
            arr = self.session.map_array
            loc = self.session.localization
            origin = self.session.map_origin
            res = self.session.map_resolution
            name = self.session.current_map_name

        self._update_map_meta_label(arr, origin, res)

        self.ax.clear()
        self.ax.set_facecolor(self.theme.MAP_BG)
        self.ax.tick_params(colors="#94a3b8", labelsize=self.theme.SZ_MAP_TICK)
        for spine in self.ax.spines.values():
            spine.set_color("#475569")
        if arr is None:
            self.ax.text(
                0.5,
                0.5,
                "No map loaded\nSLAM 页加载地图后，在本页点「刷新地图」",
                ha="center",
                va="center",
                color="#94a3b8",
                fontsize=self.theme.SZ_UI_MD,
                fontfamily=self.theme.mpl_family,
                transform=self.ax.transAxes,
            )
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw_idle()
            return

        h, w = arr.shape
        extent = [
            origin[0],
            origin[0] + w * res,
            origin[1],
            origin[1] + h * res,
        ]
        self.ax.imshow(arr, cmap="gray_r", origin="upper", extent=extent, aspect="equal")
        self.ax.grid(True, color="#475569", linestyle="--", linewidth=0.45, alpha=0.45)
        self.ax.set_xlabel("x (m)", color="#94a3b8", fontsize=self.theme.SZ_MAP_TICK)
        self.ax.set_ylabel("y (m)", color="#94a3b8", fontsize=self.theme.SZ_MAP_TICK)
        self.ax.set_title(
            name or "map",
            color=self.theme.TEXT,
            fontsize=self.theme.SZ_MAP_TITLE,
            pad=8,
            fontfamily=self.theme.mpl_family,
        )

        if loc and loc.is_localization:
            x, y = loc.pose.position[0], loc.pose.position[1]
            yaw = loc.pose.orientation[2]
            dx = 0.4 * math.cos(yaw)
            dy = 0.4 * math.sin(yaw)
            pose_color = "#34d399"
            self.ax.add_patch(
                FancyArrow(
                    x,
                    y,
                    dx,
                    dy,
                    width=0.08,
                    color=pose_color,
                    length_includes_head=True,
                )
            )
            self.ax.plot(x, y, "o", color=pose_color, ms=7)

        if self._map_init_pose:
            ix, iy, iyaw = self._map_init_pose
            self.ax.plot(ix, iy, "o", color="#fbbf24", ms=8, markeredgecolor="#fef3c7", mew=1.5)
            idx = 0.35 * math.cos(iyaw)
            idy = 0.35 * math.sin(iyaw)
            self.ax.add_patch(
                FancyArrow(
                    ix,
                    iy,
                    idx,
                    idy,
                    width=0.07,
                    color="#fbbf24",
                    length_includes_head=True,
                )
            )
        if self._map_goal_pose:
            gx, gy, gyaw = self._map_goal_pose
            self.ax.plot(gx, gy, "x", color="#f87171", ms=14, mew=2.5)
            yaw = gyaw
            gdx = 0.35 * math.cos(yaw)
            gdy = 0.35 * math.sin(yaw)
            self.ax.add_patch(
                FancyArrow(
                    gx,
                    gy,
                    gdx,
                    gdy,
                    width=0.07,
                    color="#fca5a5",
                    length_includes_head=True,
                )
            )

        self.canvas.draw_idle()

    def _update_status_labels(self) -> None:
        with self.session._lock:
            loc = self.session.localization
            nav = self.session.nav_status_msg
        if loc:
            loc_s = (
                f"Localized @ ({loc.pose.position[0]:.2f}, {loc.pose.position[1]:.2f}, "
                f"yaw={loc.pose.orientation[2]:.2f})"
                if loc.is_localization
                else "Not localized"
            )
            style = "StatusOk.TLabel" if loc.is_localization else "StatusWarn.TLabel"
            self.loc_label.config(text=f"Localization: {loc_s}", style=style)
        self.nav_label.config(text=f"Nav: {nav or '—'}")

    def _set_connection_ui(self, state: str) -> None:
        t = self.theme
        if not hasattr(self, "_conn_dot"):
            return
        if state == "ok":
            self._conn_dot.config(fg=t.SUCCESS)
            self.conn_label.config(text="Connected", style="StatusOk.TLabel")
        elif state == "fail":
            self._conn_dot.config(fg=t.DANGER)
            self.conn_label.config(text="Connection failed", style="StatusBad.TLabel")
        else:
            self._conn_dot.config(fg=t.PILL_IDLE)
            self.conn_label.config(text="Disconnected", style="StatusIdle.TLabel")

    def _on_connect(self) -> None:
        ok, msg = self.session.connect(
            self.local_ip_var.get().strip(),
            self.robot_ip_var.get().strip(),
        )
        self._log_action("Connect", ok, msg)
        if ok:
            self._set_connection_ui("ok")
            self._refresh_gait_current_ui()
            self._update_audio_status_label()
            self._update_display_status_label()
            self._update_sensor_status_labels()
            self._update_motion_robot_state_panel()
        else:
            self._set_connection_ui("fail")
            messagebox.showerror("Connect", msg)

    def _on_disconnect(self) -> None:
        if hasattr(self, "rtsp_player"):
            self.rtsp_player.stop()
            self._update_rtsp_stream_ui()
        self._on_joy_stop()
        self.session.disconnect()
        self._set_connection_ui("idle")
        self._set_gait_current_idle(disconnected=True)
        self._update_audio_status_label()
        self._update_display_status_label()
        self._update_sensor_status_labels()
        self._log_action("Disconnect", True, "已断开连接")
        self._update_motion_robot_state_panel()

    def _robot_host(self) -> str:
        if hasattr(self, "robot_ip_var"):
            return _robot_host_from_addr(self.robot_ip_var.get())
        return _robot_host_from_addr(self.default_robot_ip)

    def _default_rtsp_url(self) -> str:
        path = self.rtsp_path
        if path and not path.startswith("/"):
            path = "/" + path
        return f"rtsp://{self._robot_host()}:{self.rtsp_port}{path}"

    def _build_audio_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Audio ")
        self._audio_tab = tab
        scroll = self._scrollable_frame(tab)
        t = self.theme

        self.theme.info_box(
            scroll,
            "音量、TTS 播放与语音配置均通过 gRPC 与机载 eame_app 通信（GrpcOnly）。",
        )

        self.audio_status_label = ttk.Label(
            scroll, text="Audio: 未连接", style="StatusIdle.TLabel", wraplength=t.INFO_WRAP
        )
        self.audio_status_label.pack(anchor=tk.W, padx=t.PAD_FRAME, pady=(0, t.PAD_ROW))

        vf = ttk.LabelFrame(scroll, text=" 音量 ")
        vf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        vol_row = ttk.Frame(vf, style="Card.TFrame")
        vol_row.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        self.audio_volume_var = tk.IntVar(value=50)
        ttk.Label(vol_row, text="0", style="CardMuted.TLabel").pack(side=tk.LEFT)
        ttk.Scale(
            vol_row,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.audio_volume_var,
            length=320,
        ).pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)
        ttk.Label(vol_row, text="100", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.audio_volume_readout = ttk.Label(
            vol_row, textvariable=self.audio_volume_var, width=4, style="Card.TLabel"
        )
        self.audio_volume_readout.pack(side=tk.LEFT, padx=8)
        ttk.Button(
            vol_row,
            text="Get volume",
            command=self._wrap_action("Get volume", self._on_audio_get_volume),
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            vol_row,
            text="Set volume",
            style="Accent.TButton",
            command=self._wrap_action("Set volume", self._on_audio_set_volume),
        ).pack(side=tk.LEFT, padx=4)
        self.audio_volume_status = ttk.Label(
            vf, text="当前音量：—", style="CardMuted.TLabel", wraplength=t.INFO_WRAP
        )
        self.audio_volume_status.pack(anchor=tk.W, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))

        tf = ttk.LabelFrame(scroll, text=" TTS ")
        tf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        tts_top = ttk.Frame(tf, style="Card.TFrame")
        tts_top.pack(fill=tk.X, padx=t.PAD_INNER, pady=(t.PAD_INNER, t.PAD_ROW))
        ttk.Label(tts_top, text="ID", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.tts_id_var = tk.StringVar(value="nav_viz_001")
        ttk.Entry(tts_top, textvariable=self.tts_id_var, width=18).pack(side=tk.LEFT, padx=(6, 16))
        ttk.Label(tts_top, text="Priority", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.tts_priority_var = tk.StringVar(value="HIGH")
        ttk.Combobox(
            tts_top,
            textvariable=self.tts_priority_var,
            values=["HIGH", "MIDDLE", "LOW"],
            state="readonly",
            width=10,
        ).pack(side=tk.LEFT, padx=(6, 16))
        ttk.Label(tts_top, text="Mode", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.tts_mode_var = tk.StringVar(value="CLEARTOP")
        ttk.Combobox(
            tts_top,
            textvariable=self.tts_mode_var,
            values=["CLEARTOP", "ADD", "CLEARBUFFER"],
            state="readonly",
            width=12,
        ).pack(side=tk.LEFT, padx=6)
        ttk.Label(tf, text="播报内容", style="CardMuted.TLabel").pack(anchor=tk.W, padx=t.PAD_INNER)
        tts_text_wrap = ttk.Frame(tf, style="Card.TFrame")
        tts_text_wrap.pack(fill=tk.X, padx=t.PAD_INNER, pady=(1, 0))
        tts_body = self.theme.scroll_body(tts_text_wrap, border=False)
        self.tts_content = tk.Text(
            tts_body, height=2, font=self.theme.font_ui, wrap=tk.WORD, relief=tk.FLAT
        )
        self.tts_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.theme.mount_scroll_rail(tts_body, self.tts_content)
        self.tts_content.insert("1.0", "你好，我是 MagicDog。")
        tts_btn = ttk.Frame(tf, style="Card.TFrame")
        tts_btn.pack(fill=tk.X, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))
        ttk.Button(
            tts_btn,
            text="Play TTS",
            style="Accent.TButton",
            command=self._wrap_action("Play TTS", self._on_audio_play_tts),
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            tts_btn,
            text="Stop",
            command=self._wrap_action("Stop TTS", self._on_audio_stop_tts),
        ).pack(side=tk.LEFT, padx=4)

        cfgf = ttk.LabelFrame(scroll, text=" 语音配置 ")
        cfgf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        cfg_row = ttk.Frame(cfgf, style="Card.TFrame")
        cfg_row.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        ttk.Button(
            cfg_row,
            text="Get voice config",
            command=self._wrap_action("Get voice config", self._on_audio_get_config),
        ).pack(side=tk.LEFT, padx=4)
        ttk.Label(cfg_row, text="TTS 模型", style="CardMuted.TLabel").pack(side=tk.LEFT, padx=(16, 4))
        self.tts_type_var = tk.StringVar(value="DOUBAO")
        ttk.Combobox(
            cfg_row,
            textvariable=self.tts_type_var,
            values=["NONE", "DOUBAO", "GOOGLE"],
            state="readonly",
            width=10,
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            cfg_row,
            text="Switch model",
            command=self._wrap_action("Switch model", self._on_audio_switch_tts),
        ).pack(side=tk.LEFT, padx=4)
        cfg_text_wrap = ttk.Frame(cfgf, style="Card.TFrame")
        cfg_text_wrap.pack(fill=tk.X, padx=t.PAD_INNER, pady=(0, t.PAD_TAB))
        cfg_body = self.theme.scroll_body(cfg_text_wrap, border=False)
        self.audio_config_text = tk.Text(
            cfg_body,
            height=3,
            font=self.theme.font_mono,
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
        )
        self.audio_config_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.theme.mount_scroll_rail(cfg_body, self.audio_config_text)
        bind_content_drag_scroll(self.audio_config_text)

    def _update_audio_status_label(self) -> None:
        if not hasattr(self, "audio_status_label"):
            return
        if not self.session.connected or not self.session.audio:
            self.audio_status_label.config(
                text="Audio: 未连接", style="StatusIdle.TLabel"
            )
            return
        self.audio_status_label.config(
            text="Audio: 已连接 · gRPC（音量 / TTS / 配置）",
            style="StatusOk.TLabel",
        )

    def _tts_priority_value(self):
        m = {
            "HIGH": magicdog.TtsPriority.HIGH,
            "MIDDLE": magicdog.TtsPriority.MIDDLE,
            "LOW": magicdog.TtsPriority.LOW,
        }
        return m.get(self.tts_priority_var.get(), magicdog.TtsPriority.HIGH)

    def _tts_mode_value(self):
        m = {
            "CLEARTOP": magicdog.TtsMode.CLEARTOP,
            "ADD": magicdog.TtsMode.ADD,
            "CLEARBUFFER": magicdog.TtsMode.CLEARBUFFER,
        }
        return m.get(self.tts_mode_var.get(), magicdog.TtsMode.CLEARTOP)

    def _tts_type_value(self):
        m = {
            "NONE": magicdog.TtsType.NONE,
            "DOUBAO": magicdog.TtsType.DOUBAO,
            "GOOGLE": magicdog.TtsType.GOOGLE,
        }
        return m.get(self.tts_type_var.get(), magicdog.TtsType.DOUBAO)

    def _set_audio_config_display(self, text: str) -> None:
        self.audio_config_text.config(state=tk.NORMAL)
        self.audio_config_text.delete("1.0", tk.END)
        self.audio_config_text.insert("1.0", text)
        self.audio_config_text.config(state=tk.DISABLED)

    def _on_audio_get_volume(self) -> None:
        ok, vol, msg = self.session.get_volume()
        if ok and vol is not None:
            self.audio_volume_var.set(vol)
            self.audio_volume_status.config(
                text=f"当前音量：{vol}", style="StatusOk.TLabel"
            )
            self._log_action("Get volume", True, f"volume={vol}")
        else:
            self.audio_volume_status.config(
                text=f"当前音量：查询失败 — {msg}", style="StatusBad.TLabel"
            )
            self._log_action("Get volume", False, msg)

    def _on_audio_set_volume(self) -> None:
        vol = int(self.audio_volume_var.get())
        ok, msg = self.session.set_volume(vol)
        if ok:
            self.audio_volume_status.config(
                text=f"当前音量：{vol}（已设置）", style="StatusOk.TLabel"
            )
            self._log_action("Set volume", True, f"volume={vol}")
        else:
            self._log_action("Set volume", False, msg)

    def _on_audio_play_tts(self) -> None:
        text = self.tts_content.get("1.0", tk.END).strip()
        if not text:
            self._log_action("Play TTS", False, "播报内容为空")
            return
        ok, msg = self.session.play_tts(
            text,
            self.tts_id_var.get().strip() or "nav_viz_001",
            self._tts_priority_value(),
            self._tts_mode_value(),
        )
        self._log_action("Play TTS", ok, msg)

    def _on_audio_stop_tts(self) -> None:
        ok, msg = self.session.stop_tts()
        self._log_action("Stop TTS", ok, msg)

    def _on_audio_get_config(self) -> None:
        ok, text = self.session.get_voice_config_text()
        if ok:
            self._set_audio_config_display(text)
            self._log_action("Get voice config", True, "已更新配置显示")
        else:
            self._set_audio_config_display(f"FAILED: {text}")
            self._log_action("Get voice config", False, text)

    def _on_audio_switch_tts(self) -> None:
        ok, msg = self.session.switch_tts_model(self._tts_type_value())
        self._log_action("Switch model", ok, msg)

    def _format_face_expression(self, face: object) -> str:
        name = (getattr(face, "name", None) or "").strip()
        desc = (getattr(face, "description", None) or "").strip()
        fid = int(getattr(face, "id", -1))
        line = f"id={fid}"
        if name:
            line += f"  {name}"
        if desc:
            line += f"\n{desc}"
        return line

    def _build_display_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Display ")
        self._display_tab = tab
        scroll = self._scrollable_frame(tab)
        t = self.theme

        self.theme.info_box(
            scroll,
            "LCD 表情通过 gRPC（getAllFaceExpressions / setFaceExpression / getFaceExpression）控制，"
            "无需 LCM。Connect 后刷新列表并设置表情 ID。",
        )

        self.display_status_label = ttk.Label(
            scroll, text="Display: 未连接", style="StatusIdle.TLabel", wraplength=t.INFO_WRAP
        )
        self.display_status_label.pack(anchor=tk.W, padx=t.PAD_FRAME, pady=(0, t.PAD_ROW))

        curf = ttk.LabelFrame(scroll, text=" 当前表情 ")
        curf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        self.display_current_label = ttk.Label(
            curf, text="—", style="Card.TLabel", wraplength=t.INFO_WRAP
        )
        self.display_current_label.pack(anchor=tk.W, padx=t.PAD_INNER, pady=t.PAD_INNER)
        cur_btn = ttk.Frame(curf, style="Card.TFrame")
        cur_btn.pack(fill=tk.X, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))
        ttk.Button(
            cur_btn,
            text="Get current",
            command=self._wrap_action("Get current face", self._on_display_get_current),
        ).pack(side=tk.LEFT, padx=4)

        listf = ttk.LabelFrame(scroll, text=" 表情列表 ")
        listf.pack(fill=tk.BOTH, expand=True, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        list_panel, self.display_face_list = self.theme.listbox_panel(listf, height=7)
        list_panel.pack(fill=tk.BOTH, expand=True, padx=t.PAD_INNER, pady=t.PAD_INNER)
        self.display_face_list.bind("<<ListboxSelect>>", self._on_display_list_select)

        self.display_detail_label = ttk.Label(
            listf, text="", style="CardMuted.TLabel", wraplength=t.INFO_WRAP
        )
        self.display_detail_label.pack(anchor=tk.W, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))

        list_btn = ttk.Frame(listf, style="Card.TFrame")
        list_btn.pack(fill=tk.X, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))
        ttk.Button(
            list_btn,
            text="Refresh list",
            style="Accent.TButton",
            command=self._wrap_action("Refresh face list", self._on_display_refresh_list),
        ).pack(side=tk.LEFT, padx=4)

        setf = ttk.LabelFrame(scroll, text=" 设置表情 ")
        setf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=(t.PAD_ROW, t.PAD_TAB))
        set_row = ttk.Frame(setf, style="Card.TFrame")
        set_row.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        ttk.Label(set_row, text="ID", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.display_face_id_var = tk.StringVar(value="16")
        ttk.Entry(set_row, textvariable=self.display_face_id_var, width=8).pack(
            side=tk.LEFT, padx=(6, 12)
        )
        ttk.Button(
            set_row,
            text="← 选中项",
            command=self._on_display_use_selected_id,
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            set_row,
            text="Set face",
            style="Accent.TButton",
            command=self._wrap_action("Set face expression", self._on_display_set_face),
        ).pack(side=tk.LEFT, padx=8)

        self._display_faces_by_index: List[object] = []

    def _build_sensor_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Sensor ")
        scroll = self._scrollable_frame(tab)
        t = self.theme

        self.theme.info_box(
            scroll,
            "通过 gRPC 打开/关闭传感器硬件与数据通道（不含数据订阅）。"
            "建议先 Open 数据通道，再按需打开激光雷达、RGBD 或双目相机；"
            "Disconnect 时会自动全部关闭。",
        )

        self.sensor_status_label = ttk.Label(
            scroll, text="Sensor: 未连接", style="StatusIdle.TLabel", wraplength=t.INFO_WRAP
        )
        self.sensor_status_label.pack(anchor=tk.W, padx=t.PAD_FRAME, pady=(0, t.PAD_ROW))

        self._sensor_row_labels: dict[str, ttk.Label] = {}
        for key, title, detail in SENSOR_HW_ROWS:
            self._sensor_hw_row(scroll, key, title, detail)

        util = ttk.LabelFrame(scroll, text=" 批量 ")
        util.pack(fill=tk.X, padx=t.PAD_FRAME, pady=(t.PAD_ROW, t.PAD_TAB))
        util_row = ttk.Frame(util, style="Card.TFrame")
        util_row.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        ttk.Button(
            util_row,
            text="全部关闭",
            style="Muted.TButton",
            command=self._wrap_action("Close all sensors", self._on_sensor_close_all),
        ).pack(side=tk.LEFT, padx=4)

    def _sensor_hw_row(self, parent: tk.Widget, key: str, title: str, detail: str) -> None:
        t = self.theme
        rowf = ttk.LabelFrame(parent, text=f" {title} ")
        rowf.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_ROW)
        inner = ttk.Frame(rowf, style="Card.TFrame")
        inner.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        ttk.Label(
            inner, text=detail, style="CardMuted.TLabel", wraplength=t.INFO_WRAP
        ).pack(anchor=tk.W)

        btn_row = ttk.Frame(inner, style="Card.TFrame")
        btn_row.pack(fill=tk.X, pady=(t.PAD_ROW, 0))
        status_lbl = ttk.Label(btn_row, text="—", style="StatusIdle.TLabel")
        status_lbl.pack(side=tk.LEFT, padx=(0, 12))
        self._sensor_row_labels[key] = status_lbl

        ttk.Button(
            btn_row,
            text="Open",
            style="Accent.TButton",
            command=self._wrap_action(
                f"Open {title}", lambda k=key: self._on_sensor_open(k)
            ),
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            btn_row,
            text="Close",
            style="Muted.TButton",
            command=self._wrap_action(
                f"Close {title}", lambda k=key: self._on_sensor_close(k)
            ),
        ).pack(side=tk.LEFT, padx=4)

    def _update_sensor_status_labels(self) -> None:
        if not hasattr(self, "sensor_status_label"):
            return
        if not self.session.connected:
            self.sensor_status_label.config(
                text="Sensor: 未连接", style="StatusIdle.TLabel"
            )
            for lbl in getattr(self, "_sensor_row_labels", {}).values():
                lbl.config(text="—", style="StatusIdle.TLabel")
            return
        if not self.session.sensor:
            self.sensor_status_label.config(
                text="Sensor: 控制器不可用（数据通道开关仍可使用）",
                style="StatusWarn.TLabel",
            )
        else:
            self.sensor_status_label.config(
                text="Sensor: 已连接 · gRPC（硬件开关）",
                style="StatusOk.TLabel",
            )
        state = self.session.get_sensor_state()
        for key, lbl in self._sensor_row_labels.items():
            if state.get(key):
                lbl.config(text="OPEN", style="StatusOk.TLabel")
            else:
                lbl.config(text="CLOSED", style="StatusIdle.TLabel")

    def _on_sensor_open(self, key: str) -> None:
        ok, msg = self.session.open_sensor_hw(key)
        self._update_sensor_status_labels()
        self._log_action(f"Open {key}", ok, msg)

    def _on_sensor_close(self, key: str) -> None:
        ok, msg = self.session.close_sensor_hw(key)
        self._update_sensor_status_labels()
        self._log_action(f"Close {key}", ok, msg)

    def _on_sensor_close_all(self) -> None:
        for key in ("binocular_camera", "rgbd_camera", "laser_scan", "channel"):
            ok, msg = self.session.close_sensor_hw(key)
            self._log_action(f"Close {key}", ok, msg)
        self._update_sensor_status_labels()

    def _update_display_status_label(self) -> None:
        if not hasattr(self, "display_status_label"):
            return
        if not self.session.connected or not self.session.display:
            self.display_status_label.config(
                text="Display: 未连接", style="StatusIdle.TLabel"
            )
            return
        self.display_status_label.config(
            text="Display: 已连接 · gRPC（表情列表 / 设置 / 查询）",
            style="StatusOk.TLabel",
        )

    def _on_display_list_select(self, _event=None) -> None:
        sel = self.display_face_list.curselection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self._display_faces_by_index):
            self.display_detail_label.config(
                text=self._format_face_expression(self._display_faces_by_index[idx])
            )

    def _on_display_use_selected_id(self) -> None:
        sel = self.display_face_list.curselection()
        if not sel:
            self._log_action("← 选中项", False, "请先在列表中选择表情")
            return
        idx = int(sel[0])
        if idx < 0 or idx >= len(self._display_faces_by_index):
            return
        face = self._display_faces_by_index[idx]
        self.display_face_id_var.set(str(int(face.id)))
        self._show_action_feedback("← 选中项", True, f"id={face.id}")

    def _on_display_refresh_list(self) -> None:
        ok, faces, msg = self.session.get_all_face_expressions()
        self.display_face_list.delete(0, tk.END)
        self._display_faces_by_index = []
        if not ok:
            self.display_detail_label.config(text="")
            self._log_action("Refresh face list", False, msg)
            return
        self._display_faces_by_index = sorted(faces, key=lambda f: int(f.id))
        for face in self._display_faces_by_index:
            name = (face.name or "").strip() or "—"
            self.display_face_list.insert(tk.END, f"{face.id:4d}  {name}")
        self._log_action("Refresh face list", True, f"{len(faces)} expressions")
        if self._display_faces_by_index:
            self.display_face_list.selection_set(0)
            self._on_display_list_select()

    def _on_display_get_current(self) -> None:
        ok, face, msg = self.session.get_current_face_expression()
        if ok and face is not None:
            text = self._format_face_expression(face)
            self.display_current_label.config(text=text, style="StatusOk.TLabel")
            self.display_face_id_var.set(str(int(face.id)))
            self._log_action("Get current face", True, f"id={face.id} {face.name or ''}".strip())
        else:
            self.display_current_label.config(
                text=f"查询失败 — {msg}", style="StatusBad.TLabel"
            )
            self._log_action("Get current face", False, msg)

    def _on_display_set_face(self) -> None:
        try:
            expr_id = int(self.display_face_id_var.get().strip())
        except ValueError:
            self._log_action("Set face expression", False, "ID 须为整数")
            return
        ok, msg = self.session.set_face_expression(expr_id)
        if ok:
            self._on_display_get_current()
        self._log_action("Set face expression", ok, msg or f"id={expr_id}")

    def _build_video_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Video ")

        if not _HAS_RTSP_DEPS:
            self.theme.info_box(
                tab,
                "需要安装 opencv-python 与 Pillow：pip install -r requirements.txt",
                wraplength=800,
            )
            return

        self.theme.info_box(
            tab,
            "机器人相机 RTSP 预览（左）+ 虚拟摇杆（右），默认 rtsp://<机器人IP>:8082。"
            "边看画面边控狗；摇杆与 Motion 页共用一条 20Hz 推流。",
        )
        t = self.theme

        ctrl = ttk.LabelFrame(tab, text=" RTSP ")
        ctrl.pack(fill=tk.X, padx=t.PAD_FRAME, pady=t.PAD_INNER)
        row = ttk.Frame(ctrl, style="Card.TFrame")
        row.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_INNER)
        ttk.Label(row, text="URL", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.rtsp_url_var = tk.StringVar(value=self._default_rtsp_url())
        ttk.Entry(row, textvariable=self.rtsp_url_var, width=52).pack(
            side=tk.LEFT, padx=8, fill=tk.X, expand=True
        )
        ttk.Button(
            row,
            text="同步机器人 IP",
            command=self._wrap_action("同步机器人 IP", self._on_rtsp_sync_ip),
        ).pack(side=tk.LEFT, padx=4)

        btn_row = ttk.Frame(ctrl, style="Card.TFrame")
        btn_row.pack(fill=tk.X, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))
        self.rtsp_start_btn = ttk.Button(
            btn_row,
            text="▶  Start",
            style="Accent.TButton",
            command=self._wrap_action("RTSP Start", self._on_rtsp_start),
        )
        self.rtsp_start_btn.pack(side=tk.LEFT, padx=4)
        self.rtsp_stop_btn = ttk.Button(
            btn_row,
            text="■  Stop",
            style="Muted.TButton",
            command=self._wrap_action("RTSP Stop", self._on_rtsp_stop),
            state=tk.DISABLED,
        )
        self.rtsp_stop_btn.pack(side=tk.LEFT, padx=4)
        self.rtsp_status_pill = self.theme.make_pill(
            btn_row, "  已停止  ", bg=self.theme.PILL_IDLE
        )
        self.rtsp_status_pill.pack(side=tk.LEFT, padx=8)
        self.rtsp_status_label = ttk.Label(btn_row, text="未连接 RTSP", style="CardMuted.TLabel")
        self.rtsp_status_label.pack(side=tk.LEFT, padx=4)

        body = ttk.Frame(tab)
        body.pack(fill=tk.BOTH, expand=True, padx=t.PAD_FRAME, pady=(0, t.PAD_TAB))
        paned = tk.PanedWindow(body, orient=tk.HORIZONTAL)
        self.theme.paned_config(paned)
        paned.pack(fill=tk.BOTH, expand=True)

        preview_wrap = ttk.Frame(paned)
        joy_wrap = ttk.Frame(paned)
        paned.add(preview_wrap, minsize=360)
        paned.add(joy_wrap, minsize=220)

        self._video_view = ttk.LabelFrame(preview_wrap, text=" Preview ")
        self._video_view.pack(fill=tk.BOTH, expand=True)
        self.rtsp_preview_border = tk.Frame(
            self._video_view,
            bg=self.theme.BG,
            highlightthickness=3,
            highlightbackground=self.theme.BORDER,
        )
        self.rtsp_preview_border.pack(fill=tk.BOTH, expand=True, padx=t.PAD_INNER, pady=t.PAD_INNER)
        self.rtsp_label = tk.Label(
            self.rtsp_preview_border,
            text="No stream",
            bg="#0f172a",
            fg="#94a3b8",
            font=self.theme.font_ui,
        )
        self.rtsp_label.pack(fill=tk.BOTH, expand=True)

        stats_bar = tk.Frame(self._video_view, bg=self.theme.SURFACE_ALT)
        stats_bar.pack(fill=tk.X, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))
        self.rtsp_stats_label = tk.Label(
            stats_bar,
            text=RtspStreamStats.idle_text(),
            bg=self.theme.SURFACE_ALT,
            fg=self.theme.TEXT_MUTED,
            font=self.theme.font_mono,
            anchor=tk.W,
            justify=tk.LEFT,
            padx=6,
            pady=4,
        )
        self.rtsp_stats_label.pack(fill=tk.X)

        self.rtsp_player = RtspPlayer(
            self.root,
            self.rtsp_label,
            self._log,
            on_stats=self._on_rtsp_stats,
            on_failed=self._on_rtsp_open_failed,
        )

        self._build_video_joy_panel(joy_wrap)

        self._video_tab = tab
        self.notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_changed)
        self._update_rtsp_stream_ui()

    def _build_video_joy_panel(self, parent: ttk.Frame) -> None:
        self._video_joy_frame = ttk.LabelFrame(parent, text=" 摇杆 · 20 Hz ")
        self._video_joy_frame.pack(fill=tk.BOTH, expand=True)
        video_joy_scroll = self._scrollable_frame(self._video_joy_frame)
        t = self.theme

        self.video_joy_sticks_border = tk.Frame(
            video_joy_scroll,
            bg=self.theme.BG,
            highlightthickness=2,
            highlightbackground=self.theme.BORDER,
        )
        self.video_joy_sticks_border.pack(pady=t.PAD_INNER, padx=t.PAD_INNER, fill=tk.X)

        sticks = ttk.Frame(self.video_joy_sticks_border)
        sticks.pack(pady=t.PAD_INNER)

        stick_size = t.JOY_SIZE
        self.video_left_stick = VirtualJoystick(
            sticks,
            size=stick_size,
            label="左：横移 / 前进",
        )
        self.video_left_stick.pack(side=tk.LEFT, padx=10)

        self.video_right_stick = VirtualJoystick(
            sticks,
            size=stick_size,
            label="右：转向",
            horizontal_only=True,
        )
        self.video_right_stick.pack(side=tk.LEFT, padx=10)

        bf = ttk.Frame(video_joy_scroll, style="Card.TFrame")
        bf.pack(fill=tk.X, padx=t.PAD_INNER, pady=t.PAD_ROW)
        self.video_joy_start_btn = ttk.Button(
            bf,
            text="▶  Start stream",
            style="Accent.TButton",
            command=self._wrap_action(
                "Start stream", lambda: self._on_joy_start("video")
            ),
        )
        self.video_joy_start_btn.pack(side=tk.LEFT, padx=4, pady=t.PAD_ROW)
        self.video_joy_stop_btn = ttk.Button(
            bf,
            text="■  Stop",
            style="Muted.TButton",
            command=self._wrap_action("Stop stream", self._on_joy_stop),
            state=tk.DISABLED,
        )
        self.video_joy_stop_btn.pack(side=tk.LEFT, padx=4, pady=t.PAD_ROW)

        status_row = ttk.Frame(video_joy_scroll, style="Card.TFrame")
        status_row.pack(fill=tk.X, padx=t.PAD_INNER, pady=(0, t.PAD_INNER))
        self.video_joy_status_pill = self.theme.make_pill(
            status_row, "  已停止  ", bg=self.theme.PILL_IDLE
        )
        self.video_joy_status_pill.pack(anchor=tk.W, padx=4, pady=2)
        self.video_joy_status_label = ttk.Label(
            status_row,
            text="未向机器人发送摇杆指令",
            style="CardMuted.TLabel",
            wraplength=260,
        )
        self.video_joy_status_label.pack(anchor=tk.W, padx=4, pady=(0, 6))

        ttk.Label(
            video_joy_scroll,
            text="按住摇杆移动；须先 Connect。与 Motion 页同时仅一路推流。",
            style="CardHint.TLabel",
            wraplength=280,
        ).pack(padx=t.PAD_ROW, pady=(0, t.PAD_ROW))

    def _joy_ui_targets(self) -> List[dict]:
        targets = []
        if hasattr(self, "joy_start_btn"):
            targets.append(
                {
                    "start_btn": self.joy_start_btn,
                    "stop_btn": self.joy_stop_btn,
                    "pill": self.joy_status_pill,
                    "label": self.joy_status_label,
                    "border": self.joy_sticks_border,
                    "frame": self._joy_frame,
                    "frame_title_idle": " Virtual joysticks · 20 Hz ",
                    "frame_title_active": " Virtual joysticks · 推流中 ",
                }
            )
        if hasattr(self, "video_joy_start_btn"):
            targets.append(
                {
                    "start_btn": self.video_joy_start_btn,
                    "stop_btn": self.video_joy_stop_btn,
                    "pill": self.video_joy_status_pill,
                    "label": self.video_joy_status_label,
                    "border": self.video_joy_sticks_border,
                    "frame": self._video_joy_frame,
                    "frame_title_idle": " 摇杆 · 20 Hz ",
                    "frame_title_active": " 摇杆 · 推流中 ",
                }
            )
        return targets

    def _on_rtsp_open_failed(self, message: str) -> None:
        self._update_rtsp_stream_ui()
        if self._rtsp_start_pending_log:
            self._log_action("RTSP Start", False, message)
            self._rtsp_start_pending_log = False

    def _on_rtsp_stats(self, stats: RtspStreamStats) -> None:
        if hasattr(self, "rtsp_stats_label"):
            self.rtsp_stats_label.config(text=stats.summary())

    def _refresh_rtsp_stats_label(self) -> None:
        if not hasattr(self, "rtsp_stats_label"):
            return
        if hasattr(self, "rtsp_player") and self.rtsp_player.status == "Playing":
            self.rtsp_stats_label.config(text=self.rtsp_player.get_stats().summary())
        else:
            self.rtsp_stats_label.config(text=RtspStreamStats.idle_text())

    def _on_rtsp_sync_ip(self) -> None:
        self.rtsp_url_var.set(self._default_rtsp_url())
        self._log_action("同步机器人 IP", True, self.rtsp_url_var.get())

    def _on_rtsp_start(self) -> None:
        if not hasattr(self, "rtsp_player"):
            self._log_action("RTSP Start", False, "播放器未初始化")
            return
        if self.rtsp_player.is_active:
            self._log_action("RTSP Start", False, "请先 Stop 当前流再重新连接")
            return
        url = self.rtsp_url_var.get().strip()
        if self.rtsp_player.start(url):
            self._rtsp_start_pending_log = True
            self._update_rtsp_stream_ui()
            self._schedule_rtsp_status()
        else:
            self._log_action("RTSP Start", False, "无法启动播放器")

    def _on_rtsp_stop(self) -> None:
        if hasattr(self, "rtsp_player"):
            self.rtsp_player.stop()
            self._rtsp_start_pending_log = False
            self._update_rtsp_stream_ui()
            self._log_action("RTSP Stop", True, "已停止")

    def _schedule_rtsp_status(self) -> None:
        self._update_rtsp_stream_ui()
        self._refresh_rtsp_stats_label()
        if not hasattr(self, "rtsp_player"):
            return
        player = self.rtsp_player
        st = player.status
        if self._rtsp_start_pending_log and st == "Playing":
            self._log_action(
                "RTSP Start",
                True,
                player.last_open_msg or self.rtsp_url_var.get(),
            )
            self._rtsp_start_pending_log = False
        if player.is_active or st not in ("Stopped",):
            self.root.after(500, self._schedule_rtsp_status)

    def _update_rtsp_stream_ui(self) -> None:
        if not hasattr(self, "rtsp_start_btn"):
            return
        player = self.rtsp_player
        st = player.status

        if player.is_active and st == "Playing":
            self.rtsp_start_btn.config(state=tk.DISABLED, style="Muted.TButton")
            self.rtsp_stop_btn.config(state=tk.NORMAL, style="Danger.TButton")
            self.rtsp_status_pill.config(text="  播放中  ", bg=self.theme.SUCCESS)
            self.rtsp_status_label.config(text=st, style="StatusOk.TLabel")
            self.rtsp_preview_border.config(highlightbackground=self.theme.SUCCESS)
            self._video_view.configure(text=" Preview · 播放中 ")
        elif player.is_active and st == "Connecting…":
            self.rtsp_start_btn.config(state=tk.DISABLED, style="Muted.TButton")
            self.rtsp_stop_btn.config(state=tk.NORMAL, style="Danger.TButton")
            self.rtsp_status_pill.config(text="  连接中…  ", bg=self.theme.WARN)
            self.rtsp_status_label.config(text="正在连接 RTSP", style="StatusWarn.TLabel")
            self.rtsp_preview_border.config(highlightbackground=self.theme.WARN)
            self._video_view.configure(text=" Preview · 连接中 ")
        elif st in ("Open failed", "Read error"):
            self.rtsp_start_btn.config(state=tk.NORMAL, style="Accent.TButton")
            self.rtsp_stop_btn.config(state=tk.DISABLED, style="Muted.TButton")
            self.rtsp_status_pill.config(text="  异常  ", bg=self.theme.DANGER)
            err = player.last_error or st
            short_err = err if len(err) <= 80 else err[:77] + "…"
            self.rtsp_status_label.config(text=short_err, style="StatusBad.TLabel")
            self.rtsp_preview_border.config(highlightbackground=self.theme.DANGER)
            self._video_view.configure(text=" Preview ")
        else:
            self.rtsp_start_btn.config(state=tk.NORMAL, style="Accent.TButton")
            self.rtsp_stop_btn.config(state=tk.DISABLED, style="Muted.TButton")
            self.rtsp_status_pill.config(text="  已停止  ", bg=self.theme.PILL_IDLE)
            self.rtsp_status_label.config(text="未连接 RTSP", style="CardMuted.TLabel")
            self.rtsp_preview_border.config(highlightbackground=self.theme.BORDER)
            self._video_view.configure(text=" Preview ")
        self._refresh_rtsp_stats_label()

    def _on_notebook_tab_changed(self, _event=None) -> None:
        if not hasattr(self, "rtsp_player") or not hasattr(self, "_video_tab"):
            return
        try:
            selected = self.notebook.nametowidget(self.notebook.select())
        except tk.TclError:
            return
        if selected is not self._video_tab and self.rtsp_player.is_active:
            self.rtsp_player.stop()
            self._update_rtsp_stream_ui()

    def _on_close(self) -> None:
        self._on_joy_stop()
        if hasattr(self, "rtsp_player"):
            self.rtsp_player.stop()
            self._update_rtsp_stream_ui()
        self.session.disconnect()
        self.root.destroy()

    def _on_gait_selected(self, *_args) -> None:
        self.gait_desc_label.config(text=_choice_desc(GAIT_CHOICES, self.gait_var.get()))

    def _on_trick_selected(self, *_args) -> None:
        self.trick_desc_label.config(text=_choice_desc(TRICK_CHOICES, self.trick_var.get()))

    def _gait_value(self):
        return _choice_value(GAIT_CHOICES, self.gait_var.get())

    def _trick_value(self):
        return _choice_value(TRICK_CHOICES, self.trick_var.get())

    def _set_gait_current_idle(self, disconnected: bool = False) -> None:
        if not hasattr(self, "gait_current_label"):
            return
        if disconnected:
            text = "当前步态：— （未连接）"
        else:
            text = "当前步态：— （连接后点击 Get gait 查询）"
        self.gait_current_label.config(text=text, style="StatusIdle.TLabel")

    def _apply_gait_current_ui(self, ok: bool, gait: Optional[object], msg: str) -> None:
        if not hasattr(self, "gait_current_label"):
            return
        if ok and gait is not None:
            last = self.session._last_gait
            text, row, _fallback = _format_gait_status(gait, last)
            self.gait_current_label.config(text=text, style="StatusOk.TLabel")
            if row:
                self.gait_var.set(row[0])
                self.gait_desc_label.config(text=row[2])
        else:
            detail = msg or "unknown error"
            self.gait_current_label.config(
                text=f"当前步态：查询失败 — {detail}",
                style="StatusBad.TLabel",
            )

    def _refresh_gait_current_ui(self) -> None:
        ok, gait, msg = self.session.get_gait()
        self._apply_gait_current_ui(ok, gait, msg)
        if ok and gait is not None:
            self._log_action("Get gait", True, _gait_log_line(gait, self.session._last_gait))
        else:
            self._log_action("Get gait", False, msg)

    def _on_set_gait(self) -> None:
        gait = self._gait_value()
        ok, msg = self.session.set_gait(gait)
        if ok:
            self._apply_gait_current_ui(True, gait, msg)
            self._log_action("Set gait", True, _gait_log_line(gait))
        else:
            self._log_action("Set gait", False, msg)

    def _on_get_gait(self) -> None:
        if not self.session.connected:
            self._set_gait_current_idle(disconnected=False)
            self._log_action("Get gait", False, "请先 Connect")
            return
        self._refresh_gait_current_ui()

    def _on_trick(self) -> None:
        ok, msg = self.session.execute_trick(self._trick_value())
        self._log_action("Execute trick", ok, msg)

    def _update_joy_stream_ui(self, streaming: bool) -> None:
        for ui in self._joy_ui_targets():
            if streaming:
                ui["start_btn"].config(state=tk.DISABLED, style="Muted.TButton")
                ui["stop_btn"].config(state=tk.NORMAL, style="Danger.TButton")
                ui["pill"].config(text="  推流中 · 20Hz  ", bg=self.theme.SUCCESS)
                ui["label"].config(
                    text="正在发送 JoystickCommand",
                    style="StatusOk.TLabel",
                )
                ui["border"].config(highlightbackground=self.theme.SUCCESS)
                ui["frame"].configure(text=ui["frame_title_active"])
            else:
                ui["start_btn"].config(state=tk.NORMAL, style="Accent.TButton")
                ui["stop_btn"].config(state=tk.DISABLED, style="Muted.TButton")
                ui["pill"].config(text="  已停止  ", bg=self.theme.PILL_IDLE)
                ui["label"].config(
                    text="未向机器人发送摇杆指令",
                    style="CardMuted.TLabel",
                )
                ui["border"].config(highlightbackground=self.theme.BORDER)
                ui["frame"].configure(text=ui["frame_title_idle"])

    def _on_joy_start(self, source: str = "motion") -> None:
        if not self.session.connected:
            self._log_action("Start stream", False, "请先 Connect")
            messagebox.showwarning("Joystick", "Connect first")
            return
        self._joy_axes_source = source
        self.session.start_joy_loop(self._get_joy_axes)
        self._update_joy_stream_ui(True)
        where = "Video" if source == "video" else "Motion"
        self._log_action("Start stream", True, f"摇杆推流 20Hz ({where})")

    def _get_joy_axes(self) -> Tuple[float, float, float, float]:
        if self._joy_axes_source == "video" and hasattr(self, "video_left_stick"):
            lx, ly = self.video_left_stick.get_values()
            rx, _ry = self.video_right_stick.get_values()
        else:
            lx, ly = self.left_stick.get_values()
            rx, _ry = self.right_stick.get_values()
        return lx, ly, rx, 0.0

    def _on_joy_stop(self) -> None:
        self.session._stop_joy()
        if hasattr(self, "left_stick"):
            self.left_stick.reset()
            self.right_stick.reset()
        if hasattr(self, "video_left_stick"):
            self.video_left_stick.reset()
            self.video_right_stick.reset()
        self._update_joy_stream_ui(False)
        self._log_action("Stop stream", True, "摇杆推流已停止")

    def _on_joy_zero(self) -> None:
        if hasattr(self, "left_stick"):
            self.left_stick.reset()
            self.right_stick.reset()
        if hasattr(self, "video_left_stick"):
            self.video_left_stick.reset()
            self.video_right_stick.reset()

    def _slam_cmd(self, fn, name: str) -> None:
        if not self.session.slam:
            self._log_action(name, False, "请先 Connect")
            messagebox.showwarning(name, "Connect first")
            return
        try:
            st = fn()
            ok = _status_ok(st)
            self._log_action(name, ok, st.message)
        except Exception as exc:
            self._log_action(name, False, str(exc))

    def _on_start_mapping(self) -> None:
        self._slam_cmd(self.session.slam.start_mapping, "start_mapping")

    def _on_cancel_mapping(self) -> None:
        self._slam_cmd(self.session.slam.cancel_mapping, "cancel_mapping")

    def _on_save_map(self) -> None:
        name = self.save_map_name.get().strip() or f"map_{int(time.time())}"

        def _save():
            return self.session.slam.save_map(name)

        self._slam_cmd(_save, "save_map")
        self.root.after(500, self._on_refresh_maps)

    def _on_switch_loc(self) -> None:
        self._slam_cmd(self.session.slam.switch_to_location, "switch_to_location")

    def _on_slam_idle(self) -> None:
        self._slam_cmd(self.session.slam.switch_to_idle, "switch_to_idle")

    def _on_refresh_maps(self, prefer_map_name: str = "") -> None:
        ok, msg, names = self.session.refresh_maps(prefer_map_name=prefer_map_name)
        self.map_list.delete(0, tk.END)
        for n in names:
            self.map_list.insert(tk.END, n)
        self._log_action("刷新地图", ok, msg)
        if ok:
            self._redraw_map()

    def _on_load_map(self) -> None:
        sel = self.map_list.curselection()
        if not sel:
            self._log_action("加载选中", False, "请先在列表中选择地图")
            return
        name = self.map_list.get(sel[0])
        if not self.session.slam:
            self._log_action("load_map", False, "请先 Connect")
            messagebox.showwarning("load_map", "Connect first")
            return
        try:
            st = self.session.slam.load_map(name)
            ok = _status_ok(st)
            self._log_action("load_map", ok, st.message)
            if ok:
                self._map_init_pose = None
                self._map_goal_pose = None
                self.root.after(800, lambda n=name: self._on_refresh_maps(prefer_map_name=n))
        except Exception as exc:
            self._log_action("load_map", False, str(exc))

    def _on_delete_map(self) -> None:
        sel = self.map_list.curselection()
        if not sel:
            self._log_action("删除选中地图", False, "请先在列表中选择地图")
            return
        name = self.map_list.get(sel[0])
        if not messagebox.askyesno("Delete", f"Delete map '{name}'?"):
            return

        def _del():
            return self.session.slam.delete_map(name)

        self._slam_cmd(_del, "delete_map")
        self.root.after(500, self._on_refresh_maps)

    def _on_nav_on(self) -> None:
        self._slam_cmd(
            lambda: self.session.slam.activate_nav_mode(magicdog.NavMode.GRID_MAP),
            "activate_nav_mode",
        )

    def _on_nav_pause(self) -> None:
        self._slam_cmd(self.session.slam.pause_nav_task, "pause_nav")

    def _on_nav_resume(self) -> None:
        self._slam_cmd(self.session.slam.resume_nav_task, "resume_nav")

    def _on_nav_cancel(self) -> None:
        self._slam_cmd(self.session.slam.cancel_nav_task, "cancel_nav")

    def _on_nav_status(self) -> None:
        if not self.session.slam:
            self._log_action("查询导航状态", False, "请先 Connect")
            return
        st, nav = self.session.slam.get_nav_task_status()
        if _status_ok(st):
            self._log_action("查询导航状态", True, str(nav))
        else:
            self._log_action("查询导航状态", False, st.message)

    def _build_pose3d(
        self,
        x_var: tk.DoubleVar,
        y_var: tk.DoubleVar,
        yaw_var: tk.DoubleVar,
        roll_var: Optional[tk.DoubleVar] = None,
        pitch_var: Optional[tk.DoubleVar] = None,
        z: float = 0.0,
    ) -> object:
        p = magicdog.Pose3DEuler()
        p.position = [x_var.get(), y_var.get(), z]
        roll = roll_var.get() if roll_var is not None else 0.0
        pitch = pitch_var.get() if pitch_var is not None else 0.0
        p.orientation = [roll, pitch, yaw_var.get()]
        return p

    def _on_init_pose(self) -> None:
        if not self.session.slam:
            return
        p = self._build_pose3d(
            self.init_pose_x,
            self.init_pose_y,
            self.init_pose_yaw,
            self.init_pose_roll,
            self.init_pose_pitch,
        )
        st = self.session.slam.init_pose(p)
        if _status_ok(st):
            x, y = self.init_pose_x.get(), self.init_pose_y.get()
            yaw = self.init_pose_yaw.get()
            self._map_init_pose = (x, y, yaw)
            self._redraw_map()
            detail = (
                f"pos=({x:.2f},{y:.2f}) "
                f"rpy=({self.init_pose_roll.get():.2f},{self.init_pose_pitch.get():.2f},{yaw:.2f})"
            )
            self._log_action("提交 Init pose", True, detail)
        else:
            self._log_action("提交 Init pose", False, st.message)

    def _on_set_goal(self) -> None:
        if not self.session.slam or not self.session.high:
            return
        self.session.set_gait(magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS)
        self.session.high.disable_joy_stick()
        self._on_joy_stop()
        tgt = magicdog.NavTarget()
        tgt.id = 1
        tgt.frame_id = "map"
        tgt.goal = self._build_pose3d(
            self.goal_pose_x, self.goal_pose_y, self.goal_pose_yaw
        )
        st = self.session.slam.set_nav_target(tgt)
        self.session.high.enable_joy_stick()
        if _status_ok(st):
            gx, gy = self.goal_pose_x.get(), self.goal_pose_y.get()
            gyaw = self.goal_pose_yaw.get()
            self._map_goal_pose = (gx, gy, gyaw)
            self._redraw_map()
            self._log_action(
                "导航到目标点",
                True,
                f"({gx:.2f},{gy:.2f}) yaw={gyaw:.2f}",
            )
        else:
            self._log_action("导航到目标点", False, st.message)

    def _on_copy_init_pose(self) -> None:
        with self.session._lock:
            loc = self.session.localization
        if not loc:
            self._log_action("填入定位位姿", False, "无定位数据")
            return
        self.init_pose_x.set(loc.pose.position[0])
        self.init_pose_y.set(loc.pose.position[1])
        ori = loc.pose.orientation
        if len(ori) >= 3:
            self.init_pose_roll.set(ori[0])
            self.init_pose_pitch.set(ori[1])
            self.init_pose_yaw.set(ori[2])
        if loc.is_localization:
            self._map_init_pose = (
                loc.pose.position[0],
                loc.pose.position[1],
                ori[2] if len(ori) >= 3 else 0.0,
            )
            self._redraw_map()
        self._log_action("填入定位位姿", True, "已写入初始位姿 X/Y/RPY")

    def _on_copy_goal_yaw(self) -> None:
        with self.session._lock:
            loc = self.session.localization
        if not loc or len(loc.pose.orientation) < 3:
            self._log_action("目标 Yaw ← 定位", False, "无定位 yaw")
            return
        yaw = loc.pose.orientation[2]
        self.goal_pose_yaw.set(yaw)
        self._log_action("目标 Yaw ← 定位", True, f"yaw={yaw:.3f} rad")

    def _anchor_xy_for_map_mode(self, mode: str) -> Tuple[float, float]:
        if mode == "init":
            return self.init_pose_x.get(), self.init_pose_y.get()
        return self.goal_pose_x.get(), self.goal_pose_y.get()

    def _apply_map_pose(
        self,
        mode: str,
        x: float,
        y: float,
        yaw: Optional[float] = None,
        *,
        submit: bool = False,
        quiet: bool = False,
    ) -> None:
        x = round(x, 3)
        y = round(y, 3)
        if mode == "init":
            self.init_pose_x.set(x)
            self.init_pose_y.set(y)
            if yaw is not None:
                self.init_pose_yaw.set(round(yaw, 4))
            yaw_v = self.init_pose_yaw.get()
            self._map_init_pose = (x, y, yaw_v)
            if not quiet:
                if yaw is not None:
                    self._show_action_feedback(
                        "地图·初始朝向",
                        True,
                        f"({x:.2f},{y:.2f}) yaw={yaw_v:.2f} rad",
                    )
                else:
                    self._show_action_feedback(
                        "地图·初始位置",
                        True,
                        f"({x:.2f}, {y:.2f})",
                    )
            if submit:
                self._on_init_pose()
        else:
            self.goal_pose_x.set(x)
            self.goal_pose_y.set(y)
            if yaw is not None:
                self.goal_pose_yaw.set(round(yaw, 4))
            yaw_v = self.goal_pose_yaw.get()
            self._map_goal_pose = (x, y, yaw_v)
            if not quiet:
                if yaw is not None:
                    self._show_action_feedback(
                        "地图·目标朝向",
                        True,
                        f"({x:.2f},{y:.2f}) yaw={yaw_v:.2f} rad",
                    )
                else:
                    self._show_action_feedback(
                        "地图·目标位置",
                        True,
                        f"({x:.2f}, {y:.2f})",
                    )
            if submit:
                self._on_set_goal()
        self._redraw_map()

    def _on_map_click_mode_changed(self) -> None:
        mode = "导航目标" if self.map_click_mode.get() == "goal" else "初始位姿"
        self._show_action_feedback("地图点击模式", True, mode)

    def _on_map_press(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        mode = self.map_click_mode.get()
        x = float(event.xdata)
        y = float(event.ydata)
        btn = getattr(event, "button", 1)

        if btn == 1:
            if getattr(event, "dblclick", False):
                self._apply_map_pose(mode, x, y, submit=True)
            else:
                self._apply_map_pose(mode, x, y)
        elif btn == 3:
            ax, ay = self._anchor_xy_for_map_mode(mode)
            self._map_rotate = {"mode": mode, "ax": ax, "ay": ay}
            yaw = math.atan2(y - ay, x - ax)
            self._apply_map_pose(mode, ax, ay, yaw=yaw, quiet=True)

    def _on_map_motion(self, event) -> None:
        if not self._map_rotate or event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None:
            return
        r = self._map_rotate
        yaw = math.atan2(float(event.ydata) - r["ay"], float(event.xdata) - r["ax"])
        self._apply_map_pose(r["mode"], r["ax"], r["ay"], yaw=yaw, quiet=True)

    def _on_map_release(self, event) -> None:
        if getattr(event, "button", None) != 3:
            return
        if not self._map_rotate:
            return
        r = self._map_rotate
        self._map_rotate = None
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        yaw = math.atan2(float(event.ydata) - r["ay"], float(event.xdata) - r["ax"])
        self._apply_map_pose(r["mode"], r["ax"], r["ay"], yaw=yaw)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="MagicDog gRPC-only nav GUI")
    parser.add_argument("--local-ip", default="192.168.55.10", help="PC IP on robot network")
    parser.add_argument("--robot-ip", default="192.168.55.200", help="eame_app gRPC host")
    parser.add_argument("--rtsp-port", type=int, default=8082, help="RTSP port on robot")
    parser.add_argument(
        "--rtsp-path",
        default="",
        help="RTSP path suffix on Video tab, e.g. /stream",
    )
    args = parser.parse_args()
    app = NavVizApp(
        args.local_ip,
        args.robot_ip,
        rtsp_port=args.rtsp_port,
        rtsp_path=args.rtsp_path,
    )
    app.run()


if __name__ == "__main__":
    main()
