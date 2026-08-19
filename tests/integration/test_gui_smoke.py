"""Fumaça da GUI — só roda quando há display e Tk."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("tkinter")

pytestmark = pytest.mark.skipif(
    os.name != "nt" and not os.environ.get("DISPLAY"),
    reason="GUI exige DISPLAY (ou Windows)",
)


def test_aplicativo_abre_e_fecha():
    from telas_em_pixels.app import Aplicativo

    app = Aplicativo()
    try:
        app.update()
        app.update_idletasks()
        assert app.winfo_exists()
        assert len(app.monitores) >= 1
        assert app.overlay.winfo_exists()
        app._iniciar_overlay()
        app.update_idletasks()
        assert app.overlay.visivel()
    finally:
        app.destroy()
