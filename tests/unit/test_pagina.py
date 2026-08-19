"""Tamanhos de página, orientação e escala."""

import pytest

from telas_em_pixels.dominio.pagina import (
    TAMANHOS_PAGINA,
    escala_para_caber,
    pagina_em_pontos,
)


def test_a4_retrato_mais_alto_que_largo():
    w, h = pagina_em_pontos("A4", "retrato")
    assert w < h
    assert abs(w - 595.27) < 1
    assert abs(h - 841.89) < 1


def test_a4_paisagem_inverte():
    wr, hr = pagina_em_pontos("A4", "retrato")
    wp, hp = pagina_em_pontos("A4", "paisagem")
    assert wp == hr and hp == wr
    assert wp > hp


def test_todos_os_tamanhos_tem_retrato_e_paisagem():
    for nome in TAMANHOS_PAGINA:
        wr, hr = pagina_em_pontos(nome, "retrato")
        wp, hp = pagina_em_pontos(nome, "paisagem")
        assert wr <= hr
        assert wp >= hp
        assert {wr, hr} == {wp, hp}


def test_tamanho_ou_orientacao_invalidos():
    with pytest.raises(ValueError):
        pagina_em_pontos("Oficio", "retrato")
    with pytest.raises(ValueError):
        pagina_em_pontos("A4", "landscape")


def test_escala_limitada_pela_largura():
    s = escala_para_caber(1920, 1080, 800, 800)
    assert s == pytest.approx(800 / 1920)
    assert 1920 * s <= 800 + 1e-6
    assert 1080 * s <= 800 + 1e-6


def test_escala_limitada_pela_altura():
    s = escala_para_caber(100, 400, 500, 200)
    assert s == pytest.approx(0.5)


def test_escala_origem_invalida():
    with pytest.raises(ValueError):
        escala_para_caber(0, 10, 100, 100)
