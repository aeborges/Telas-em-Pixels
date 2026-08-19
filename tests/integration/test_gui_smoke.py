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
        assert app.mapa.winfo_exists()
        assert "x" in app.painel.ponteiro_var.get().lower()
        app._tick_ponteiro()
        app.update_idletasks()
        texto = app.painel.ponteiro_var.get()
        assert "x" in texto.lower()
        assert not hasattr(app, "overlay")  # tela cobrindo o monitor foi removida
    finally:
        app.destroy()


def test_mapa_surge_ao_definir_dois_pontos():
    from telas_em_pixels.dominio.geometria import Ponto
    from telas_em_pixels.app import Aplicativo

    app = Aplicativo()
    try:
        app.update()
        app.painel.definir_pontos(Ponto(0, 0), Ponto(199, 99))
        app.update_idletasks()
        assert app._ultima_selecao is not None
        _global, local = app._ultima_selecao
        assert local.largura == 200
        assert local.altura == 100
        estilo = app.painel.estilo_grade()
        assert estilo.cor_principal == "#BDBDBD"
        assert estilo.cor_secundaria == "#D6D6D6"
    finally:
        app.destroy()
