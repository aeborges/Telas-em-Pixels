"""PDF gerado: cabeçalho %PDF e MediaBox retrato/paisagem."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

from telas_em_pixels.dominio.geometria import Retangulo
from telas_em_pixels.dominio.pagina import pagina_em_pontos
from telas_em_pixels.dominio.pdf import gerar_mapa_pdf
from telas_em_pixels.dominio.regua import EstiloGrade

_MEDIA = re.compile(
    rb"/MediaBox\s*\[\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*\]"
)


def _mediabox(data: bytes) -> tuple[float, float]:
    achado = _MEDIA.search(data)
    assert achado, "MediaBox não encontrado no PDF"
    return float(achado.group(3)), float(achado.group(4))


def test_pdf_paisagem_a4(tmp_path: Path):
    dest = tmp_path / "paisagem.pdf"
    gerar_mapa_pdf(
        dest,
        Retangulo(0, 0, 400, 200),
        tamanho_pagina="A4",
        orientacao="paisagem",
        titulo="Teste paisagem",
    )
    data = dest.read_bytes()
    assert data.startswith(b"%PDF")
    w, h = _mediabox(data)
    ew, eh = pagina_em_pontos("A4", "paisagem")
    assert abs(w - ew) < 1
    assert abs(h - eh) < 1
    assert w > h


def test_pdf_retrato_letter(tmp_path: Path):
    dest = tmp_path / "retrato.pdf"
    gerar_mapa_pdf(
        dest,
        Retangulo(10, 20, 120, 300),
        tamanho_pagina="Letter",
        orientacao="retrato",
        origem_x=10,
        origem_y=20,
    )
    data = dest.read_bytes()
    assert data.startswith(b"%PDF")
    w, h = _mediabox(data)
    ew, eh = pagina_em_pontos("Letter", "retrato")
    assert abs(w - ew) < 1
    assert abs(h - eh) < 1
    assert h > w


def test_pdf_com_captura(tmp_path: Path):
    dest = tmp_path / "com-foto.pdf"
    img = Image.new("RGB", (80, 40), "#CCD0EE")
    gerar_mapa_pdf(
        dest,
        Retangulo(0, 0, 80, 40),
        tamanho_pagina="A5",
        orientacao="paisagem",
        captura=img,
        titulo="Com captura",
    )
    data = dest.read_bytes()
    assert data.startswith(b"%PDF")
    assert dest.stat().st_size > 1500


def test_pdf_com_estilo_de_grade(tmp_path: Path):
    dest = tmp_path / "grade-custom.pdf"
    gerar_mapa_pdf(
        dest,
        Retangulo(0, 0, 200, 100),
        tamanho_pagina="A5",
        orientacao="paisagem",
        estilo=EstiloGrade(
            passo_menor=20,
            passo_maior=50,
            cor_principal="#BDBDBD",
            cor_secundaria="#D6D6D6",
        ),
    )
    data = dest.read_bytes()
    assert data.startswith(b"%PDF")
