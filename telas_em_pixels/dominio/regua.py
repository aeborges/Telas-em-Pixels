"""Marcas de régua e estilo visual da grade de pixels."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Cinza 74 e cinza 84 (X11 gray74 / gray84)
COR_PRINCIPAL_PADRAO = "#BDBDBD"
COR_SECUNDARIA_PADRAO = "#D6D6D6"

_HEX = re.compile(r"^#?[0-9A-Fa-f]{6}$")


def marcas_no_intervalo(inicio: int, tamanho: int, passo: int) -> list[int]:
    """Múltiplos de `passo` em `[inicio, inicio + tamanho)`.

    Usado no mapa da janela e no PDF (origem da região, que pode não
    ser múltipla do passo).
    """
    if passo <= 0 or tamanho <= 0:
        return []
    fim = inicio + tamanho
    resto = inicio % passo
    primeiro = inicio if resto == 0 else inicio + (passo - resto)
    if primeiro >= fim:
        return []
    return list(range(primeiro, fim, passo))


def normalizar_cor_hex(cor: str) -> str:
    """Aceita `RRGGBB` ou `#RRGGBB` e devolve `#RRGGBB` em maiúsculas."""
    texto = cor.strip()
    if not _HEX.match(texto):
        raise ValueError(f"Cor hexadecimal inválida: {cor!r}")
    if not texto.startswith("#"):
        texto = f"#{texto}"
    return texto.upper()


@dataclass(frozen=True, slots=True)
class EspecificacaoRegua:
    passo_menor: int = 10
    passo_maior: int = 100

    def __post_init__(self) -> None:
        if self.passo_menor < 1 or self.passo_maior < 1:
            raise ValueError("Passos da grade devem ser ≥ 1 px")

    def menores(self, inicio: int, tamanho: int) -> list[int]:
        return marcas_no_intervalo(inicio, tamanho, self.passo_menor)

    def maiores(self, inicio: int, tamanho: int) -> list[int]:
        return marcas_no_intervalo(inicio, tamanho, self.passo_maior)


@dataclass(frozen=True, slots=True)
class EstiloGrade:
    """Distâncias e cores das linhas principais (escuras) e secundárias."""

    passo_menor: int = 10
    passo_maior: int = 100
    cor_principal: str = COR_PRINCIPAL_PADRAO
    cor_secundaria: str = COR_SECUNDARIA_PADRAO

    def __post_init__(self) -> None:
        if self.passo_menor < 1 or self.passo_maior < 1:
            raise ValueError("Passos da grade devem ser ≥ 1 px")
        object.__setattr__(
            self, "cor_principal", normalizar_cor_hex(self.cor_principal)
        )
        object.__setattr__(
            self, "cor_secundaria", normalizar_cor_hex(self.cor_secundaria)
        )

    @property
    def spec(self) -> EspecificacaoRegua:
        return EspecificacaoRegua(self.passo_menor, self.passo_maior)
