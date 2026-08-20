"""Posição do ponteiro e estado do botão esquerdo (melhor esforço)."""

from __future__ import annotations

import sys


def posicao_cursor() -> tuple[int, int] | None:
    """Coordenada global do ponteiro, ou None se a API local falhar."""
    if sys.platform == "win32":
        return _posicao_windows()
    return None


def botao_esquerdo_pressionado() -> bool:
    """True se o botão esquerdo está abaixo. Fora do Windows, False."""
    if sys.platform != "win32":
        return False
    import ctypes

    VK_LBUTTON = 0x01
    return bool(ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)


def tecla_escape_pressionada() -> bool:
    if sys.platform != "win32":
        return False
    import ctypes

    VK_ESCAPE = 0x1B
    return bool(ctypes.windll.user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000)


def _posicao_windows() -> tuple[int, int] | None:
    import ctypes
    from ctypes import wintypes

    ponto = wintypes.POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(ponto)):
        return None
    return int(ponto.x), int(ponto.y)
