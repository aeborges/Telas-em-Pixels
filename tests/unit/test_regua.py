"""Marcas de régua 10 / 100 px e estilo da grade."""

import pytest

from telas_em_pixels.dominio.regua import (
    COR_PRINCIPAL_PADRAO,
    COR_SECUNDARIA_PADRAO,
    EspecificacaoRegua,
    EstiloGrade,
    marcas_no_intervalo,
    normalizar_cor_hex,
)


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


def test_passo_invalido_na_especificacao():
    with pytest.raises(ValueError):
        EspecificacaoRegua(passo_menor=0, passo_maior=100)
    with pytest.raises(ValueError):
        EstiloGrade(passo_menor=10, passo_maior=0)


def test_estilo_padrao_cinza_74_e_84():
    estilo = EstiloGrade()
    assert estilo.cor_principal == COR_PRINCIPAL_PADRAO == "#BDBDBD"
    assert estilo.cor_secundaria == COR_SECUNDARIA_PADRAO == "#D6D6D6"
    assert estilo.passo_menor == 10
    assert estilo.passo_maior == 100


def test_estilo_passos_e_cores_customizados():
    estilo = EstiloGrade(
        passo_menor=25,
        passo_maior=50,
        cor_principal="bdbdbd",
        cor_secundaria="#d6d6d6",
    )
    assert estilo.spec.menores(0, 80) == [0, 25, 50, 75]
    assert estilo.spec.maiores(0, 80) == [0, 50]
    assert estilo.cor_principal == "#BDBDBD"
    assert estilo.cor_secundaria == "#D6D6D6"


def test_normalizar_cor_hex():
    assert normalizar_cor_hex("#bdbdbd") == "#BDBDBD"
    assert normalizar_cor_hex("D6D6D6") == "#D6D6D6"
    with pytest.raises(ValueError):
        normalizar_cor_hex("xyz")
    with pytest.raises(ValueError):
        EstiloGrade(cor_principal="vermelho")
