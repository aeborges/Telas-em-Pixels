"""Pontos e retângulos em pixels (eixo Y para baixo)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Ponto:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class Retangulo:
    """Retângulo eixo-alinhado, inclusivo nos dois cantos.

    `largura` e `altura` contam pixels: o canto (x + largura - 1,
    y + altura - 1) ainda pertence à região. `x2`/`y2` são exclusivos
    (iguais a x+largura / y+altura), úteis em intervalos semiabertos.
    """

    x: int
    y: int
    largura: int
    altura: int

    def __post_init__(self) -> None:
        if self.largura < 1 or self.altura < 1:
            raise ValueError("Retângulo precisa ter pelo menos 1×1 pixel")

    @property
    def x2(self) -> int:
        return self.x + self.largura

    @property
    def y2(self) -> int:
        return self.y + self.altura

    @classmethod
    def de_dois_pontos(cls, a: Ponto, b: Ponto) -> Retangulo:
        """Menor retângulo que inclui os dois pixels, ordem irrelevante."""
        x = min(a.x, b.x)
        y = min(a.y, b.y)
        largura = abs(a.x - b.x) + 1
        altura = abs(a.y - b.y) + 1
        return cls(x, y, largura, altura)

    def contem_ponto(self, p: Ponto) -> bool:
        return self.x <= p.x < self.x2 and self.y <= p.y < self.y2

    def intersecao(self, outro: Retangulo) -> Retangulo | None:
        ix1 = max(self.x, outro.x)
        iy1 = max(self.y, outro.y)
        ix2 = min(self.x2, outro.x2)
        iy2 = min(self.y2, outro.y2)
        if ix2 <= ix1 or iy2 <= iy1:
            return None
        return Retangulo(ix1, iy1, ix2 - ix1, iy2 - iy1)

    def traduzir(self, dx: int, dy: int) -> Retangulo:
        return Retangulo(self.x + dx, self.y + dy, self.largura, self.altura)
