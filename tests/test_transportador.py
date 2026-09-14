import pytest

from celular_robo.excecoes import ConfiguracaoInvalida
from celular_robo.fabrica import criar_robo_configurado
from celular_robo.modelo_features import TIPOS_VALIDOS
from celular_robo.observadores import DespachanteTransporte, EquipeDeTestes, MonitorBandeja
from celular_robo.robo import RoboColetor, RoboTransportador
from celular_robo.robo_base import Robo


def test_metaprogramacao_registra_robo_transportador_automaticamente():
    assert "RoboTransportador" in Robo._registro
    assert Robo._registro["RoboTransportador"] is RoboTransportador
    assert "RoboTransportador" in TIPOS_VALIDOS


def test_lps_robo_transportador_exclui_area_quarentena():
    with pytest.raises(ConfiguracaoInvalida, match="exclui"):
        criar_robo_configurado("RoboTransportador", "Transp-1", area_nome="area_quarentena")


def test_lps_robo_transportador_valido_em_centro_padrao():
    transp = criar_robo_configurado("RoboTransportador", "Transp-1", area_nome="centro_padrao")
    assert isinstance(transp, RoboTransportador)
    assert (transp.x, transp.y) == (0, 0)
    assert len(transp.carga) == 0


def test_transportador_carregar_e_levar_ate_retirada():
    transp = criar_robo_configurado("RoboTransportador", "Transp-1", estrategia_nome="direta", area_nome="centro_padrao", ponto_retirada=(9, 9))
    transp.carregar({"Projeto Aurora": 2, "Projeto Vesper": 1})
    assert len(transp) == 3
    assert transp.carga["Projeto Aurora"] == 2

    sucesso = transp.transportar_ate_retirada()
    assert sucesso is True
    assert (transp.x, transp.y) == (9, 9)
    assert len(transp) == 0


def test_handoff_coletor_para_transportador_via_observer():
    equipe = EquipeDeTestes()
    monitor = MonitorBandeja()
    transportador = criar_robo_configurado("RoboTransportador", "Transp-Handoff", estrategia_nome="direta", area_nome="centro_padrao", ponto_retirada=(9, 9))
    despachante = DespachanteTransporte(transportador=transportador)

    coletor = criar_robo_configurado("RoboColetor", "Coletor-Handoff", observadores=[equipe, monitor, despachante])

    coletor.coletar("Projeto Aurora")
    coletor.coletar("Projeto Aurora")
    coletor.notificar("bandeja_pronta")

    assert len(coletor.bandeja) == 2

    equipe.aprovar(coletor)

    assert len(coletor.bandeja) == 0
    assert despachante.ultimo_transporte_sucesso is True
    assert (transportador.x, transportador.y) == (9, 9)
