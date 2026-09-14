# Modelo de features / LPS — enunciado, Seção 2.4.
#
# TODO: implemente aqui. TIPOS_VALIDOS, ESTRATEGIAS_VALIDAS (derivados dos
# registros de Seção 2.2, não digitados à mão), REQUER/EXCLUI (4 dimensões: tipo,
# estratégia, área, urgência) e validar_configuracao levantando
# ConfiguracaoInvalida antes de qualquer robô ser instanciado.

from celular_robo.estrategias import RotaColeta
from celular_robo.excecoes import ConfiguracaoInvalida
from celular_robo.robo import RoboColetor
from celular_robo.robo_base import Robo

AREAS: dict[str, set[tuple[int, int]]] = {
    "centro_padrao": set(),
    "area_quarentena": {(1, 1), (1, 2)}
}

TIPOS_VALIDOS: set[str] = set(Robo._registro)
ESTRATEGIAS_VALIDAS: set[str] = set(RotaColeta._registro)
AREAS_VALIDAS: set[str] = set(AREAS.keys())

EXCLUI: dict[str, set[str]] = {
    "area_quarentena": {"direta", "RotaDireta"},
    "urgente": {"fragil"}
}

REQUER: dict[str, set[str]] = {
    "fragil": {"dupla_conferencia", "RotaComDuplaConferencia"},
    "urgente": {"direta", "RotaDireta"}
}


def validar_configuracao(tipo_nome: str, estrategia_nome: str, area_nome: str) -> bool:
    """
    Valida se a combinação de tipo, estratégia e área respeita as restrições da LPS.

    Verifica se os componentes informados estão cadastrados no registro de tipos válidos e se não violam nenhuma regra de exclusão mútua (por exemplo, uso de rota direta na área de quarentena).
    Args:
        tipo_nome: Nome do tipo de robô a ser instanciado (deve constar em `TIPOS_VALIDOS`).
        estrategia_nome: Identificador da estratégia de navegação (deve constar em `ESTRATEGIAS_VALIDAS`).
        area_nome: Nome da área do laboratório (deve constar em `AREAS_VALIDAS`).

    Returns:
        True se a configuração for consistente com todas as regras do modelo.

    Raises:
        ConfiguracaoInvalida: Se o tipo de robô, a estratégia ou a área não forem válidos, ou se a área selecionada excluir mutuamente a estratégia informada.
    """
    if tipo_nome not in TIPOS_VALIDOS:
        raise ConfiguracaoInvalida(f"Tipo de robô inválido: {tipo_nome!r}. Válidos: {TIPOS_VALIDOS}")

    if estrategia_nome not in ESTRATEGIAS_VALIDAS:
        raise ConfiguracaoInvalida(f"Estratégia inválida: {estrategia_nome!r}. Válidas: {ESTRATEGIAS_VALIDAS}")

    if area_nome not in AREAS_VALIDAS:
        raise ConfiguracaoInvalida(f"Área inválida: {area_nome!r}. Válidas: {AREAS_VALIDAS}")

    if area_nome in EXCLUI and estrategia_nome in EXCLUI[area_nome]:
        raise ConfiguracaoInvalida(f"{area_nome=} exclui {estrategia_nome=}")

    return True
