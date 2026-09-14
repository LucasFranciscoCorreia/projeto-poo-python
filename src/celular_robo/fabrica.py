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
    """
    Cria e configura um robô coletor do tipo especificado.

    Args:
        tipo_nome: Nome do tipo de robô a ser criado (ex: "RoboColetor").
        nome: Nome identificador único do robô.
        **kwargs: Parâmetros adicionais para inicialização do robô.

    Returns:
        Instância do robô coletor configurado.
    """
    return criar_robo(tipo_nome, nome, **kwargs)


def criar_robo_configurado(tipo_nome: str, nome: str, estrategia_nome: str = "direta", area_nome: str = "centro_padrao", observadores: list[Observador] | None = None, **kwargs):
    """
    Cria um robô com configuração completa baseada em tipo, estratégia e área.

    Realiza validações prévias de configuração, monta a estratégia e os observadores desejados, e então cria o robô com as configurações resultantes.

    Args:
        tipo_nome: Nome do tipo de robô a ser criado (ex: "RoboColetor").
        nome: Nome identificador único do robô.
        estrategia_nome: Nome da estratégia de movimentação a ser associada. Padrão é "direta".
        area_nome: Nome da área padrão que define os obstáculos do robô. Padrão é "centro_padrao".
        observadores: Lista de observadores a serem anexados ao robô. Se None, utiliza os observadores padrão.
        **kwargs: Parâmetros adicionais para inicialização do robô.

    Returns:
        Instância do robô configurado.
    """
    validar_configuracao(tipo_nome, estrategia_nome, area_nome)
    classe_estrategia = RotaColeta._registro[estrategia_nome]
    estrategia = classe_estrategia()

    obstaculos = kwargs.pop("obstaculos", AREAS.get(area_nome, {}))

    if observadores is None:
        observadores = [MonitorBandeja(), RegistroAuditoria(), EquipeDeTestes()]

    return criar_robo_coletor(tipo_nome, nome, estrategia=estrategia, obstaculos=obstaculos, observadores=observadores, **kwargs)
