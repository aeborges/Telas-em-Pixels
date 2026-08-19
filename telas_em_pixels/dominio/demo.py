"""PDF sintético para validar o domínio sem GUI."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from telas_em_pixels.dominio.geometria import Retangulo
from telas_em_pixels.dominio.pdf import gerar_mapa_pdf


def gerar_demo_pdf(destino: str | Path) -> Path:
    ret = Retangulo(120, 80, 800, 500)
    img = Image.new("RGB", (ret.largura, ret.altura), "#EEF0F6")
    desenho = ImageDraw.Draw(img)
    desenho.rectangle(
        (8, 8, ret.largura - 9, ret.altura - 9), outline="#5B5FEF", width=2
    )
    desenho.text((24, 24), "Demo — Telas em Pixels", fill="#1E2130")
    return gerar_mapa_pdf(
        destino,
        ret,
        tamanho_pagina="A4",
        orientacao="paisagem",
        captura=img,
        titulo="Mapa de pixels — demonstração",
        origem_x=ret.x,
        origem_y=ret.y,
        metadados={"monitor": "Monitor sintético 800×500"},
    )
