"""Modelo e enumeração dos monitores do desktop virtual."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from telas_em_pixels.dominio.geometria import Ponto, Retangulo


@dataclass(frozen=True, slots=True)
class Monitor:
    indice: int
    nome: str
    x: int
    y: int
    largura: int
    altura: int
    primario: bool = False

    @property
    def rotulo(self) -> str:
        geo = f"{self.largura}×{self.altura}"
        extra = " · primário" if self.primario else ""
        return f"Monitor {self.indice + 1} — {geo}{extra}"

    @property
    def retangulo(self) -> Retangulo:
        return Retangulo(self.x, self.y, self.largura, self.altura)

    def para_local(self, x_global: int, y_global: int) -> Ponto | None:
        p = Ponto(x_global, y_global)
        if not self.retangulo.contem_ponto(p):
            return None
        return Ponto(x_global - self.x, y_global - self.y)

    def recortar_local(self, ret_global: Retangulo) -> Retangulo | None:
        inter = self.retangulo.intersecao(ret_global)
        if inter is None:
            return None
        return inter.traduzir(-self.x, -self.y)


def listar_monitores(tk_root=None) -> list[Monitor]:
    """Sempre devolve pelo menos um monitor (fallback de tela única)."""
    encontrados = _via_screeninfo() or _via_windows()
    if encontrados:
        return encontrados
    return _via_tk(tk_root)


def _via_screeninfo() -> list[Monitor]:
    try:
        from screeninfo import get_monitors
    except Exception:
        return []
    try:
        brutos = list(get_monitors())
    except Exception:
        return []
    if not brutos:
        return []
    monitores = []
    for i, m in enumerate(brutos):
        primario = bool(getattr(m, "is_primary", False))
        nome = getattr(m, "name", None) or f"Monitor {i + 1}"
        monitores.append(
            Monitor(
                indice=i,
                nome=str(nome),
                x=int(m.x),
                y=int(m.y),
                largura=int(m.width),
                altura=int(m.height),
                primario=primario,
            )
        )
    if not any(m.primario for m in monitores):
        primeiro = monitores[0]
        monitores[0] = Monitor(
            primeiro.indice,
            primeiro.nome,
            primeiro.x,
            primeiro.y,
            primeiro.largura,
            primeiro.altura,
            True,
        )
    return monitores


def _via_windows() -> list[Monitor]:
    if sys.platform != "win32":
        return []
    import ctypes
    from ctypes import wintypes

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD),
        ]

    MONITORINFOF_PRIMARY = 1
    user32 = ctypes.windll.user32
    coletados: list[tuple[int, int, int, int, bool]] = []

    @ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        wintypes.LPARAM,
    )
    def _cb(hmon, _hdc, _lprc, _lp):  # noqa: ANN001
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if user32.GetMonitorInfoW(hmon, ctypes.byref(info)):
            r = info.rcMonitor
            coletados.append(
                (
                    int(r.left),
                    int(r.top),
                    int(r.right - r.left),
                    int(r.bottom - r.top),
                    bool(info.dwFlags & MONITORINFOF_PRIMARY),
                )
            )
        return True

    if not user32.EnumDisplayMonitors(None, None, _cb, 0):
        return []
    return [
        Monitor(i, f"Monitor {i + 1}", x, y, w, h, prim)
        for i, (x, y, w, h, prim) in enumerate(coletados)
        if w > 0 and h > 0
    ]


def _via_tk(tk_root=None) -> list[Monitor]:
    largura, altura = 1920, 1080
    if tk_root is not None:
        try:
            largura = int(tk_root.winfo_screenwidth())
            altura = int(tk_root.winfo_screenheight())
        except Exception:
            pass
    else:
        try:
            import tkinter as tk

            tmp = tk.Tk()
            tmp.withdraw()
            largura = int(tmp.winfo_screenwidth())
            altura = int(tmp.winfo_screenheight())
            tmp.destroy()
        except Exception:
            pass
    return [Monitor(0, "Monitor 1", 0, 0, max(largura, 1), max(altura, 1), True)]
