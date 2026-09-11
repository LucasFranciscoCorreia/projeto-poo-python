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

from celular_robo.estrategias import RotaColeta
from celular_robo.fabrica_base import criar_robo
from celular_robo.modelo_features import AREAS, validar_configuracao
from celular_robo.observadores import EquipeDeTestes, MonitorBandeja, RegistroAuditoria
from celular_robo.observadores_base import Observador


def criar_robo_coletor(tipo_nome: str, nome: str, **kwargs):
    return criar_robo(tipo_nome, nome, **kwargs)


def criar_robo_configurado(tipo_nome: str, nome: str, estrategia_nome: str = "direta", area_nome: str = "centro_padrao", observadores: list[Observador] | None = None, **kwargs):
    validar_configuracao(tipo_nome, estrategia_nome, area_nome)
    classe_estrategia = RotaColeta._registro[estrategia_nome]
    estrategia = classe_estrategia()

    obstaculos = kwargs.pop("obstaculos", AREAS.get(area_nome, {}))

    if observadores is None:
        observadores = [MonitorBandeja(), RegistroAuditoria(), EquipeDeTestes()]

    return criar_robo_coletor(tipo_nome, nome, estrategia=estrategia, obstaculos=obstaculos, observadores=observadores, **kwargs)
