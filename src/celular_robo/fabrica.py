# Factory — criar_robo_coletor, criar_robo_configurado — enunciado, Seção 2.3.
# (Ver fabrica_base.py — genérico do curso, não editar: criar_robo("RoboColetor",
# ...) já funciona, pode chamar direto ou usar como modelo.)
#
# TODO: implemente aqui. criar_robo_coletor(tipo_nome, ...) a partir do
# _registro (Seção 2.2); criar_robo_configurado combina isso com a validação do
# modelo de features (Seção 2.4).
#
# Contrato mínimo exigido por tests/test_00_fornecido.py (não altere a
# assinatura abaixo sem também atualizar aquele arquivo):
#
#   criar_robo_configurado(tipo_nome, nome, estrategia_nome=..., area_nome=...)

from celular_robo.observadores import EquipeDeTestes
from celular_robo.observadores import RegistroAuditoria
from celular_robo.observadores import MonitorBandeja
from celular_robo.modelo_features import AREAS
from celular_robo.estrategias import RotaColeta
from celular_robo.fabrica_base import criar_robo
from celular_robo.modelo_features import validar_configuracao

def criar_robo_coletor(tipo_nome, nome, **kwargs):
    return criar_robo(tipo_nome, nome, **kwargs)

def criar_robo_configurado(tipo_nome, nome, estrategia_nome="direta", area_nome="centro_padrao", observadores=None, **kwargs):
    validar_configuracao(tipo_nome, estrategia_nome, area_nome)
    classe_estrategia = RotaColeta._registro[estrategia_nome]
    estrategia = classe_estrategia()

    obstaculos = AREAS.get(area_nome, {})

    if observadores is None:
        observadores = [MonitorBandeja(), RegistroAuditoria(), EquipeDeTestes()]
        
    return criar_robo_coletor(tipo_nome, nome, estrategia=estrategia, obstaculos=obstaculos, observadores=observadores, **kwargs)

