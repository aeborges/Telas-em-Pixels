"""Faz a janela Tk ignorar cliques (as janelas de baixo recebem o input)."""

from __future__ import annotations

import ctypes
import ctypes.util
import sys


def definir_atravessavel(janela, atravessar: bool) -> None:
    """Melhor esforço por plataforma. No-op se a API local não existir."""
    janela.update_idletasks()
    if sys.platform == "win32":
        _windows(janela, atravessar)
    elif sys.platform == "darwin":
        _macos(janela, atravessar)
    else:
        _x11(janela, atravessar)


def _hwnds(janela) -> list[int]:
    user32 = ctypes.windll.user32
    hwnd = int(janela.winfo_id())
    vistos = []
    atual = hwnd
    for _ in range(6):
        if not atual or atual in vistos:
            break
        vistos.append(atual)
        atual = int(user32.GetParent(atual) or 0)
    raiz = int(user32.GetAncestor(hwnd, 2) or 0)  # GA_ROOT
    if raiz and raiz not in vistos:
        vistos.append(raiz)
    return vistos


def _windows(janela, atravessar: bool) -> None:
    user32 = ctypes.windll.user32
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_NOACTIVATE = 0x08000000
    for hwnd in _hwnds(janela):
        estilo = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        estilo |= WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        if atravessar:
            estilo |= WS_EX_TRANSPARENT
        else:
            estilo &= ~WS_EX_TRANSPARENT
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, estilo)


class _XRectangle(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_short),
        ("y", ctypes.c_short),
        ("width", ctypes.c_ushort),
        ("height", ctypes.c_ushort),
    ]


def _x11(janela, atravessar: bool) -> None:
    libx11 = ctypes.util.find_library("X11")
    libxext = ctypes.util.find_library("Xext")
    if not libx11 or not libxext:
        return
    x11 = ctypes.cdll.LoadLibrary(libx11)
    xext = ctypes.cdll.LoadLibrary(libxext)
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XFlush.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    xext.XShapeCombineRectangles.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]
    ShapeInput = 2
    ShapeSet = 0
    Unsorted = 0
    dpy = x11.XOpenDisplay(None)
    if not dpy:
        return
    try:
        xid = int(janela.winfo_id())
        if atravessar:
            xext.XShapeCombineRectangles(
                dpy, xid, ShapeInput, 0, 0, None, 0, ShapeSet, Unsorted
            )
        else:
            rect = _XRectangle(0, 0, janela.winfo_width(), janela.winfo_height())
            xext.XShapeCombineRectangles(
                dpy,
                xid,
                ShapeInput,
                0,
                0,
                ctypes.byref(rect),
                1,
                ShapeSet,
                Unsorted,
            )
        x11.XFlush(dpy)
    finally:
        x11.XCloseDisplay(dpy)


def _macos(janela, atravessar: bool) -> None:
    try:
        import objc  # type: ignore
    except Exception:
        return
    try:
        nsview = objc.objc_object(c_void_p=int(janela.winfo_id()))
        nswindow = nsview.window()
        if nswindow is None:
            return
        nswindow.setIgnoresMouseEvents_(bool(atravessar))
        nswindow.setAcceptsMouseMovedEvents_(not atravessar)
    except Exception:
        return
