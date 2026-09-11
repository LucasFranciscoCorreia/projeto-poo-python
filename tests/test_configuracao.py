# TODO: seus testes de configuração/LPS — enunciado, Seção 2.7 (pytest.raises,
# @pytest.mark.parametrize cobrindo estratégia×área).

import pytest

from celular_robo.fabrica import criar_robo_configurado
from celular_robo.excecoes import ConfiguracaoInvalida
from celular_robo.estrategias import RotaDireta, RotaComDuplaConferencia
from celular_robo.persistencia import montar_robo_de_config

@pytest.mark.parametrize("estrategia_nome, area_nome, classe_estrategia_esperada, tem_obstaculos", [
    ("direta", "centro_padrao", RotaDireta, False),
    ("dupla_conferencia", "centro_padrao", RotaComDuplaConferencia, False),
    ("dupla_conferencia", "area_quarentena", RotaComDuplaConferencia, True),
])
def test_contrato_combinacoes_estrategia_area(estrategia_nome, area_nome, classe_estrategia_esperada, tem_obstaculos):
    robo = criar_robo_configurado(
        "RoboColetor", "Coletor-Teste",
        estrategia_nome=estrategia_nome,
        area_nome=area_nome
    )
    
    assert isinstance(robo.estrategia, classe_estrategia_esperada)
    assert (len(robo.obstaculos) > 0) == tem_obstaculos

def test_area_quarentena_cria_obstaculos_reais():
    robo = criar_robo_configurado(
        "RoboColetor", "Coletor-Quarentena",
        estrategia_nome="dupla_conferencia",
        area_nome="area_quarentena"
    )
    assert len(robo.obstaculos) == 2
    assert (1, 1) in robo.obstaculos and (1, 2) in robo.obstaculos

@pytest.mark.parametrize("tipo, estrategia, area", [
    ("RoboInexistente", "direta", "centro_padrao"),
    ("RoboColetor", "estrategia_invalida", "centro_padrao"),
    ("RoboColetor", "direta", "area_fantasma"),
])
def test_configuracao_com_valores_invalidos(tipo, estrategia, area):
    with pytest.raises(ConfiguracaoInvalida):
        criar_robo_configurado(tipo, "Robo-Falha", estrategia_nome=estrategia, area_nome=area)

def test_montar_robo_de_config():
    config = {
        "tipo_nome": "RoboColetor",
        "nome": "Coletor-JSON",
        "estrategia_nome": "dupla_conferencia",
        "area_nome": "centro_padrao"
    }
    robo = montar_robo_de_config(config)
    assert robo.nome == "Coletor-JSON"
    assert isinstance(robo.estrategia, RotaComDuplaConferencia)
    assert (robo.x, robo.y) == (0, 0)
