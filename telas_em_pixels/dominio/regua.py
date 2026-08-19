"""Marcas de régua: frações de 10 px e inteiros de 100 px."""

from __future__ import annotations

from dataclasses import dataclass


def marcas_no_intervalo(inicio: int, tamanho: int, passo: int) -> list[int]:
    """Múltiplos de `passo` em `[inicio, inicio + tamanho)`.

    Usado tanto no overlay (origem 0 do monitor) quanto no PDF (origem
    da região, que pode não ser múltipla do passo).
    """
    if passo <= 0 or tamanho <= 0:
        return []
    fim = inicio + tamanho
    resto = inicio % passo
    primeiro = inicio if resto == 0 else inicio + (passo - resto)
    if primeiro >= fim:
        return []
    return list(range(primeiro, fim, passo))


@dataclass(frozen=True, slots=True)
class EspecificacaoRegua:
    passo_menor: int = 10
    passo_maior: int = 100

    def menores(self, inicio: int, tamanho: int) -> list[int]:
        return marcas_no_intervalo(inicio, tamanho, self.passo_menor)

    def maiores(self, inicio: int, tamanho: int) -> list[int]:
        return marcas_no_intervalo(inicio, tamanho, self.passo_maior)
