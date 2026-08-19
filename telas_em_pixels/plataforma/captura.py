"""Captura de um retângulo do desktop virtual."""

from __future__ import annotations

from typing import Any

from telas_em_pixels.dominio.geometria import Retangulo


def capturar_retangulo(ret: Retangulo) -> Any | None:
    """Devolve uma imagem PIL RGB ou None se a captura falhar."""
    try:
        import mss
        from PIL import Image
    except Exception:
        return None
    try:
        with mss.mss() as sct:
            bruto = sct.grab(
                {
                    "left": int(ret.x),
                    "top": int(ret.y),
                    "width": int(ret.largura),
                    "height": int(ret.altura),
                }
            )
        return Image.frombytes("RGB", bruto.size, bruto.bgra, "raw", "BGRX")
    except Exception:
        return None
