"""Testes do retângulo canônico e recorte ao monitor."""

from telas_em_pixels.dominio.geometria import Ponto, Retangulo
from telas_em_pixels.plataforma.monitores import Monitor


def test_dois_pontos_ordem_irrelevante():
    a = Ponto(10, 20)
    b = Ponto(40, 5)
    r1 = Retangulo.de_dois_pontos(a, b)
    r2 = Retangulo.de_dois_pontos(b, a)
    assert r1 == r2
    assert r1.x == 10 and r1.y == 5
    assert r1.largura == 31 and r1.altura == 16


def test_mesmo_ponto_gera_1x1():
    p = Ponto(8, 8)
    r = Retangulo.de_dois_pontos(p, p)
    assert r == Retangulo(8, 8, 1, 1)
    assert r.contem_ponto(p)
    assert not r.contem_ponto(Ponto(9, 8))


def test_inclusivo_100x50():
    r = Retangulo.de_dois_pontos(Ponto(0, 0), Ponto(99, 49))
    assert r.largura == 100
    assert r.altura == 50
    assert r.contem_ponto(Ponto(99, 49))
    assert not r.contem_ponto(Ponto(100, 0))


def test_intersecao_parcial():
    a = Retangulo(0, 0, 100, 50)
    b = Retangulo(50, 25, 100, 50)
    i = a.intersecao(b)
    assert i == Retangulo(50, 25, 50, 25)


def test_intersecao_disjunta_e_borda():
    a = Retangulo(0, 0, 10, 10)
    b = Retangulo(10, 0, 5, 5)
    assert a.intersecao(b) is None
    c = Retangulo(200, 200, 10, 10)
    assert a.intersecao(c) is None


def test_recortar_local_ao_monitor():
    mon = Monitor(0, "M", x=1920, y=0, largura=1920, altura=1080, primario=False)
    global_ret = Retangulo.de_dois_pontos(Ponto(1900, 10), Ponto(2000, 110))
    local = mon.recortar_local(global_ret)
    assert local is not None
    # interseção global: x=1920..2000 (81 px), y=10..110 (101 px)
    assert local.x == 0
    assert local.y == 10
    assert local.largura == 81
    assert local.altura == 101


def test_recortar_totalmente_fora():
    mon = Monitor(0, "M", 0, 0, 800, 600, True)
    outro = Retangulo(900, 10, 50, 50)
    assert mon.recortar_local(outro) is None


def test_para_local_dentro_e_fora():
    mon = Monitor(0, "M", 100, 200, 640, 480, True)
    assert mon.para_local(100, 200) == Ponto(0, 0)
    assert mon.para_local(99, 200) is None
    assert mon.para_local(739, 679) == Ponto(639, 479)
    assert mon.para_local(740, 200) is None
