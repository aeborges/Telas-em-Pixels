"""Tokens visuais — mesma família da Paleta de Cores Tkinter."""

from telas_em_pixels.dominio.regua import (
    COR_PRINCIPAL_PADRAO,
    COR_SECUNDARIA_PADRAO,
)

BG_APP = "#F3F4F8"
BG_TOOLBAR = "#FFFFFF"
TEXT = "#1E2130"
TEXT_MUTED = "#6B7086"
BORDER = "#DADCE6"
ACCENT = "#5B5FEF"
ACCENT_SOFT = "#E7E7FC"
SUCESSO = "#2FAE72"
PERIGO = "#C0392B"

# Grade de pixels: cinza 74 (principal) e cinza 84 (secundária)
COR_GRADE_PRINCIPAL = COR_PRINCIPAL_PADRAO
COR_GRADE_SECUNDARIA = COR_SECUNDARIA_PADRAO

FONTE = "Segoe UI"


def fonte(tamanho: int, peso: str = "normal") -> tuple:
    return (FONTE, tamanho, peso)
