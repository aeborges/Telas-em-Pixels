"""Marcas de régua 10 / 100 px."""

from telas_em_pixels.dominio.regua import EspecificacaoRegua, marcas_no_intervalo


def test_marcas_a_partir_da_origem():
    assert marcas_no_intervalo(0, 250, 100) == [0, 100, 200]
    assert marcas_no_intervalo(0, 100, 100) == [0]
    assert marcas_no_intervalo(0, 10, 10) == [0]


def test_marcas_quando_origem_nao_e_multiplo():
    # região [50, 250): 100 e 200
    assert marcas_no_intervalo(50, 200, 100) == [100, 200]


def test_intervalo_vazio_ou_passo_invalido():
    assert marcas_no_intervalo(0, 0, 10) == []
    assert marcas_no_intervalo(0, 100, 0) == []
    assert marcas_no_intervalo(10, -5, 10) == []


def test_especificacao_padrao():
    spec = EspecificacaoRegua()
    assert spec.menores(0, 35) == [0, 10, 20, 30]
    assert spec.maiores(0, 250) == [0, 100, 200]
    assert spec.maiores(150, 80) == [200]  # [150, 230)


def test_sem_duplicatas_e_crescente():
    valores = marcas_no_intervalo(-30, 400, 10)
    assert valores == sorted(set(valores))
    assert all(v % 10 == 0 for v in valores)
    assert valores[0] >= -30
    assert valores[-1] < 370
