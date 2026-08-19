"""Tamanhos de página, orientação e escala para caber o mapa no PDF."""

from __future__ import annotations

from reportlab.lib.pagesizes import A3, A4, A5, elevenSeventeen, legal, letter

TAMANHOS_PAGINA: dict[str, tuple[float, float]] = {
    "A5": A5,
    "A4": A4,
    "A3": A3,
    "Letter": letter,
    "Legal": legal,
    "Tabloid": elevenSeventeen,
}

ORIENTACOES = ("retrato", "paisagem")

# reportlab entrega o par no retrato (largura < altura), salvo Tabloid
# que já vem paisagem nativo (11×17 in). Normalizamos sempre.


def _retrato_nativo(par: tuple[float, float]) -> tuple[float, float]:
    w, h = par
    return (w, h) if w <= h else (h, w)


def pagina_em_pontos(tamanho: str, orientacao: str) -> tuple[float, float]:
    if tamanho not in TAMANHOS_PAGINA:
        raise ValueError(f"Tamanho de página desconhecido: {tamanho}")
    if orientacao not in ORIENTACOES:
        raise ValueError(f"Orientação desconhecida: {orientacao}")
    w, h = _retrato_nativo(TAMANHOS_PAGINA[tamanho])
    if orientacao == "paisagem":
        return h, w
    return w, h


def escala_para_caber(
    origem_largura: float,
    origem_altura: float,
    destino_largura: float,
    destino_altura: float,
) -> float:
    if origem_largura <= 0 or origem_altura <= 0:
        raise ValueError("Dimensão de origem deve ser positiva")
    if destino_largura <= 0 or destino_altura <= 0:
        raise ValueError("Área de destino deve ser positiva")
    return min(destino_largura / origem_largura, destino_altura / origem_altura)
