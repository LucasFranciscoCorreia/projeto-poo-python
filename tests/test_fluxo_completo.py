# TODO: teste da transição ModoColetando -> ModoAguardandoVerificacao
# disparada pelo Observer quando a bandeja completa — enunciado, Seção 2.7.

import pytest

from celular_robo.fabrica import criar_robo_configurado
from celular_robo.comandos import ComandoColeta
from celular_robo.excecoes import ErroColeta
from celular_robo.modos import ModoColetando, ModoAguardandoVerificacao
from celular_robo.observadores import EquipeDeTestes, MonitorBandeja, RegistroAuditoria

def test_transicao_modo_quando_bandeja_pronta():
    robo = criar_robo_configurado("RoboColetor", "Coletor-State")
    
    assert isinstance(robo.modo, ModoColetando)

    robo.notificar("bandeja_pronta")

    assert isinstance(robo.modo, ModoAguardandoVerificacao)
    assert robo.mover() is False

def test_aprovacao_equipe_libera_robo_e_esvazia_bandeja():
    equipe = EquipeDeTestes()
    monitor = MonitorBandeja()
    robo = criar_robo_configurado("RoboColetor", "Coletor-Aprovacao", observadores=[equipe, monitor])

    robo.coletar("Projeto Aurora")
    robo.notificar("bandeja_pronta")
    assert isinstance(robo.modo, ModoAguardandoVerificacao)

    equipe.aprovar(robo)

    assert isinstance(robo.modo, ModoColetando)
    assert len(robo.bandeja) == 0

def test_rejeicao_equipe_mantem_itens_na_bandeja():
    equipe = EquipeDeTestes()
    monitor = MonitorBandeja()
    robo = criar_robo_configurado("RoboColetor", "Coletor-Rejeicao", observadores=[equipe, monitor])

    robo.coletar("Projeto Vesper")
    robo.notificar("bandeja_pronta")
    assert isinstance(robo.modo, ModoAguardandoVerificacao)

    equipe.rejeitar(robo)

    assert isinstance(robo.modo, ModoColetando)
    assert len(robo.bandeja) == 1

def test_comando_coleta_executar_e_desfazer():
    robo = criar_robo_configurado("RoboColetor", "Coletor-Cmd")
    cmd = ComandoColeta("Projeto Aurora", (2, 3), 2)

    cmd.executar(robo)
    assert (robo.x, robo.y) == (2, 3)
    assert len(robo.bandeja) == 2

    cmd.desfazer(robo)
    assert len(robo.bandeja) == 0

def test_registro_auditoria_grava_eventos():
    auditoria = RegistroAuditoria()
    robo = criar_robo_configurado("RoboColetor", "Coletor-Auditoria", observadores=[auditoria])

    robo.coletar("Projeto Aurora")
    robo.remover("Projeto Aurora")
    robo.notificar("bandeja_pronta")
    
    nomes_eventos = [reg["evento"] for reg in auditoria.registros]
    assert "coleta" in nomes_eventos
    assert "remocao" in nomes_eventos
    assert "bandeja_pronta" in nomes_eventos


def test_coleta_bloqueada_em_modo_aguardando_verificacao():
    robo = criar_robo_configurado("RoboColetor", "Coletor-Bloqueio")
    robo.notificar("bandeja_pronta")
    assert isinstance(robo.modo, ModoAguardandoVerificacao)

    cmd = ComandoColeta("Projeto Aurora", (1, 1), 1)
    with pytest.raises(ErroColeta, match="aguardando verificação"):
        cmd.executar(robo)


def test_coleta_falha_quando_bloqueada_por_obstaculo():
    robo = criar_robo_configurado("RoboColetor", "Coletor-Obstaculo", obstaculos={(1, 0): "bancada"})
    cmd = ComandoColeta("Projeto Aurora", (2, 0), 1)
    
    with pytest.raises(ErroColeta, match="não conseguiu alcançar"):
        cmd.executar(robo)
    
    assert len(robo.bandeja) == 0


def test_coleta_falha_quando_destino_fora_da_grade():
    robo = criar_robo_configurado("RoboColetor", "Coletor-Grade")
    cmd = ComandoColeta("Projeto Winrar", (10, 8), 5)
    
    with pytest.raises(ErroColeta, match="não conseguiu alcançar"):
        cmd.executar(robo)
    
    assert len(robo.bandeja) == 0


