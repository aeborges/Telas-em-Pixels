"""DPI awareness no Windows (antes de criar janelas Tk)."""

from __future__ import annotations

import sys


def aplicar_dpi_awareness() -> None:
    """Per-monitor DPI v2 — sem isso o mapa mente em escalas 125%/150%."""
    if sys.platform != "win32":
        return
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
