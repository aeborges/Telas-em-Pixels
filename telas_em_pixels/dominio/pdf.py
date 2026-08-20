"""Geração do mapa de pixels em PDF (uma página)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from telas_em_pixels.dominio.geometria import Retangulo
from telas_em_pixels.dominio.pagina import escala_para_caber, pagina_em_pontos
from telas_em_pixels.dominio.regua import EspecificacaoRegua, EstiloGrade

_TEXTO = HexColor("#1E2130")
_MUDO = HexColor("#6B7086")
_TICK = HexColor("#2A2E45")


def gerar_mapa_pdf(
    destino: str | Path,
    retangulo: Retangulo,
    *,
    tamanho_pagina: str = "A4",
    orientacao: str = "paisagem",
    captura: Any | None = None,
    titulo: str = "Mapa de pixels",
    origem_x: int | None = None,
    origem_y: int | None = None,
    metadados: dict[str, str] | None = None,
    spec: EspecificacaoRegua | None = None,
    estilo: EstiloGrade | None = None,
) -> Path:
    """Desenha o mapa da região `retangulo` numa única página.

    `origem_x`/`origem_y` são as coordenadas de tela/monitor do canto
    superior esquerdo da região (rótulos da régua). Se omitidas, usam
    `retangulo.x` / `retangulo.y`.
    """
    destino = Path(destino)
    estilo = estilo or EstiloGrade()
    spec = spec or estilo.spec
    ox_regiao = retangulo.x if origem_x is None else origem_x
    oy_regiao = retangulo.y if origem_y is None else origem_y

    w_pag, h_pag = pagina_em_pontos(tamanho_pagina, orientacao)
    c = canvas.Canvas(str(destino), pagesize=(w_pag, h_pag))
    c.setTitle(titulo)
    c.setAuthor("Telas em Pixels")
    c.setSubject(
        f"{retangulo.largura}×{retangulo.altura} px · "
        f"{tamanho_pagina} {orientacao}"
    )

    margem = 12 * mm
    cabeca = 18 * mm
    rodape = 11 * mm
    regua_esq = 14 * mm
    regua_sup = 9 * mm

    _desenhar_cabecalho(
        c,
        titulo=titulo,
        retangulo=retangulo,
        origem_x=ox_regiao,
        origem_y=oy_regiao,
        tamanho_pagina=tamanho_pagina,
        orientacao=orientacao,
        metadados=metadados or {},
        x=margem,
        y_topo=h_pag - margem,
        largura=w_pag - 2 * margem,
    )

    x0 = margem + regua_esq
    y0 = margem + rodape
    x1 = w_pag - margem
    y1 = h_pag - margem - cabeca - regua_sup
    area_w = max(1.0, x1 - x0)
    area_h = max(1.0, y1 - y0)

    escala = escala_para_caber(
        retangulo.largura, retangulo.altura, area_w, area_h
    )
    map_w = retangulo.largura * escala
    map_h = retangulo.altura * escala
    map_x = x0 + (area_w - map_w) / 2
    map_y = y0 + (area_h - map_h) / 2

    if captura is not None:
        _desenhar_captura(c, captura, map_x, map_y, map_w, map_h)

    _desenhar_grade(
        c,
        spec=spec,
        estilo=estilo,
        origem_x=ox_regiao,
        origem_y=oy_regiao,
        largura_px=retangulo.largura,
        altura_px=retangulo.altura,
        map_x=map_x,
        map_y=map_y,
        map_w=map_w,
        map_h=map_h,
        escala=escala,
        regua_esq=regua_esq,
        regua_sup=regua_sup,
    )

    escala_mm = (escala / 72.0) * 25.4
    c.setFillColor(_MUDO)
    c.setFont("Helvetica", 8)
    c.drawString(
        margem,
        margem + 2,
        f"Escala: 1 px = {escala:.3f} pt ({escala_mm:.3f} mm no papel)  ·  "
        f"Página {tamanho_pagina} {orientacao}  ·  "
        f"Região {retangulo.largura}×{retangulo.altura} px",
    )

    c.showPage()
    c.save()
    return destino


def _desenhar_cabecalho(
    c: canvas.Canvas,
    *,
    titulo: str,
    retangulo: Retangulo,
    origem_x: int,
    origem_y: int,
    tamanho_pagina: str,
    orientacao: str,
    metadados: dict[str, str],
    x: float,
    y_topo: float,
    largura: float,
) -> None:
    c.setFillColor(_TEXTO)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y_topo - 12, titulo)

    extra = metadados.get("monitor", "")
    sub = (
        f"Origem ({origem_x}, {origem_y})  ·  "
        f"{retangulo.largura}×{retangulo.altura} px  ·  "
        f"{tamanho_pagina} · {orientacao.capitalize()}"
    )
    if extra:
        sub = f"{extra}  ·  {sub}"
    c.setFillColor(_MUDO)
    c.setFont("Helvetica", 8)
    c.drawString(x, y_topo - 26, sub)
    c.setStrokeColor(HexColor("#DADCE6"))
    c.setLineWidth(0.6)
    c.line(x, y_topo - 32, x + largura, y_topo - 32)


def _desenhar_captura(c: canvas.Canvas, captura: Any, x, y, w, h) -> None:
    buf = BytesIO()
    captura.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    c.drawImage(
        ImageReader(buf),
        x,
        y,
        width=w,
        height=h,
        preserveAspectRatio=False,
        mask="auto",
    )


def _desenhar_grade(
    c: canvas.Canvas,
    *,
    spec: EspecificacaoRegua,
    estilo: EstiloGrade,
    origem_x: int,
    origem_y: int,
    largura_px: int,
    altura_px: int,
    map_x: float,
    map_y: float,
    map_w: float,
    map_h: float,
    escala: float,
    regua_esq: float,
    regua_sup: float,
) -> None:
    def pdf_x(sx: int) -> float:
        return map_x + (sx - origem_x) * escala

    def pdf_y(sy: int) -> float:
        # sy cresce para baixo na tela; PDF cresce para cima
        return map_y + map_h - (sy - origem_y) * escala

    c.saveState()
    c.setStrokeColor(_TICK)
    c.setLineWidth(0.8)
    c.rect(map_x, map_y, map_w, map_h, stroke=1, fill=0)

    menores_x = spec.menores(origem_x, largura_px)
    menores_y = spec.menores(origem_y, altura_px)
    maiores_x = spec.maiores(origem_x, largura_px)
    maiores_y = spec.maiores(origem_y, altura_px)

    desenhar_finos = escala * spec.passo_menor >= 2.0

    cor_sec = HexColor(estilo.cor_secundaria)
    cor_pri = HexColor(estilo.cor_principal)

    if desenhar_finos:
        c.setStrokeColor(cor_sec)
        c.setLineWidth(0.25)
        for mx in menores_x:
            if mx in maiores_x:
                continue
            px = pdf_x(mx)
            c.line(px, map_y, px, map_y + map_h)
        for my in menores_y:
            if my in maiores_y:
                continue
            py = pdf_y(my)
            c.line(map_x, py, map_x + map_w, py)

    c.setStrokeColor(cor_pri)
    c.setLineWidth(0.7)
    for mx in maiores_x:
        px = pdf_x(mx)
        c.line(px, map_y, px, map_y + map_h)
    for my in maiores_y:
        py = pdf_y(my)
        c.line(map_x, py, map_x + map_w, py)

    # ticks nas réguas (fora da área do mapa)
    c.setStrokeColor(_TICK)
    c.setFillColor(_TEXTO)
    c.setFont("Helvetica", 6)
    for mx in menores_x:
        px = pdf_x(mx)
        maior = mx % spec.passo_maior == 0
        tam = 7 if maior else 3.5
        c.setLineWidth(0.8 if maior else 0.4)
        c.line(px, map_y + map_h, px, map_y + map_h + tam)
        c.line(px, map_y, px, map_y - tam * 0.4)
        if maior:
            c.drawCentredString(px, map_y + map_h + tam + 1.5, str(mx))

    for my in menores_y:
        py = pdf_y(my)
        maior = my % spec.passo_maior == 0
        tam = 7 if maior else 3.5
        c.setLineWidth(0.8 if maior else 0.4)
        c.line(map_x, py, map_x - tam, py)
        c.line(map_x + map_w, py, map_x + map_w + tam * 0.4, py)
        if maior:
            c.saveState()
            c.translate(map_x - tam - 1, py)
            c.rotate(90)
            c.drawCentredString(0, 1, str(my))
            c.restoreState()

    c.restoreState()
    _ = regua_esq, regua_sup  # reservas de layout já aplicadas pelo chamador
