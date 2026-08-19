"""Tokens visuais — mesma família da Paleta de Cores Tkinter."""

BG_APP = "#F3F4F8"
BG_TOOLBAR = "#FFFFFF"
TEXT = "#1E2130"
TEXT_MUTED = "#6B7086"
BORDER = "#DADCE6"
ACCENT = "#5B5FEF"
ACCENT_SOFT = "#E7E7FC"
SUCESSO = "#2FAE72"
PERIGO = "#C0392B"

# Overlay: chroma-key no Windows (pixels exatamente nesta cor somem)
CHROMA = "#FF00FF"
COR_GRADE = "#5B5FEF"
COR_TICK = "#1E2130"
COR_TICK_CLARO = "#FFFFFF"
COR_ELASTICO = "#E63946"

FONTE = "Segoe UI"


def fonte(tamanho: int, peso: str = "normal") -> tuple:
    return (FONTE, tamanho, peso)
