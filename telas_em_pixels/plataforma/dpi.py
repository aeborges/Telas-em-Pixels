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


def area_util_tela() -> tuple[int, int, int, int]:
    """Retângulo útil do desktop (sem a barra de tarefas): x, y, largura, altura."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        rect = wintypes.RECT()
        SPI_GETWORKAREA = 48
        if ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
        ):
            return (
                int(rect.left),
                int(rect.top),
                int(rect.right - rect.left),
                int(rect.bottom - rect.top),
            )
    return 0, 0, 0, 0
