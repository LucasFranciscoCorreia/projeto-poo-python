# Strategy — RotaDireta, RotaComDuplaConferencia — enunciado, Seção 2.3.
# (Não confundir com estrategias_base.py — genérico do curso, não editar. Ao
# contrário de Command/Observer/State, aqui você NÃO herda de `Estrategia`:
# escreva sua própria base, ver TODO abaixo — motivo em estrategias_base.py.)
#
# TODO: implemente aqui. Considere uma base comum (RotaColeta) com
# __init_subclass__ registrando cada rota, ver Seção 2.2 (metaprogramação
# aplicada a uma segunda hierarquia).

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from celular_robo.robo_base import Direcao, Robo


class RotaColeta(ABC):
    """
    Classe base abstrata para as estratégias de rota e coleta do robô.

    Define o contrato de navegação até o destino e o mecanismo de coleta. Utiliza `__init_subclass__` para manter um registro automático de todas as estratégias disponíveis no sistema.

    Attributes:
        _registro: Catálogo de classes que mapeia o identificador textual para a respectiva subclasse de estratégia.
        identificador: Nome identificador da estratégia configurada.
    """
    _registro: ClassVar[dict[str, type[RotaColeta]]] = {}

    def __init_subclass__(cls, identificador: str | None = None, **kwargs) -> None:
        """
        Registra automaticamente a subclasse no catálogo de estratégias.

        Args:
            identificador: Nome identificador da estratégia no registro (ex.: 'direta'). Caso não seja informado, utiliza o nome da própria classe.
            **kwargs: Argumentos adicionais repassados para a superclasse.
        """
        super().__init_subclass__(**kwargs)
        chave: str = identificador or cls.__name__
        cls.identificador: str = chave
        RotaColeta._registro[chave] = cls

    def mover(self, robo: Robo, destino: tuple[int, int] | None = None) -> bool:
        """
        Movimenta o robô em direção a um destino específico ou avança um passo.

        Args:
            robo: Instância do robô a ser movimentado.
            destino: Coordenadas (x, y) de destino, ou None para avançar um passo na direção em que o robô está apontando.

        Returns:
            True se a movimentação foi concluída com sucesso; False caso contrário (por exemplo, colisão com obstáculo ou limites do laboratório).
        """
        if destino:
            return self._deslocar_ate(robo, destino)
        else:
            return robo.avancar()

    def _deslocar_ate(self, robo: Robo, destino: tuple[int, int]) -> bool:
        """
        Desloca o robô passo a passo na grade até atingir as coordenadas alvo.
        
        Ajusta a orientação do robô (Leste, Oeste, Norte, Sul) a cada passo e avança até alcançar o ponto desejado.
        
        Args:
            robo: Instância do robô em deslocamento.
            destino: Coordenadas (x, y) que o robô deve alcançar.

        Returns:
            True se o robô atingiu exatamente o destino; False se foi impedido no percurso por obstáculos ou limites da grade.
        """
        alvo_x, alvo_y = destino
        while (robo.x, robo.y) != (alvo_x, alvo_y):
            if robo.x < alvo_x:
                robo.girar_ate(Direcao.LESTE)
            elif robo.x > alvo_x:
                robo.girar_ate(Direcao.OESTE)
            elif robo.y < alvo_y:
                robo.girar_ate(Direcao.NORTE)
            elif robo.y > alvo_y:
                robo.girar_ate(Direcao.SUL)

            if not robo.avancar():
                return False
        return True

    @abstractmethod
    def coletar(self, robo: Robo, item: str, quantidade: int = 1):
        """
        Executa o procedimento de coleta do item pelo robô.

        Deve ser implementado pelas subclasses concretas para definir a lógica específica da estratégia.

        Args:
            robo: Instância do robô que executa a coleta.
            item: Codinome do item a ser coletado.
            quantidade: Quantidade de unidades a coletar. Padrão é 1.
        """
        ...


class RotaDireta(RotaColeta, identificador="direta"):
    """
    Estratégia de coleta direta sem etapas intermediárias de verificação.
    
    Coleta os itens sequencialmente chamando diretamente o método de coleta do robô.
    """
    def coletar(self, robo: Robo, item: str, quantidade: int = 1):
        """
        Coleta as unidades do item diretamente para a bandeja do robô.

        Args:
            robo: Instância do robô que executa a coleta.
            item: Codinome do item a ser coletado.
            quantidade: Quantidade de unidades a coletar. Padrão é 1.
        """
        for _ in range(quantidade):
            robo.coletar(item)


class RotaComDuplaConferencia(RotaColeta, identificador="dupla_conferencia"):
    """
    Estratégia de coleta com dupla conferência para itens frágeis ou críticos.
    
    Emite notificações de auditoria ('dupla_conferencia') aos observadores registrados no robô antes de efetivar cada unidade na bandeja.
    """
    def coletar(self, robo: Robo, item: str, quantidade: int = 1):
        """
        Coleta as unidades do item notificando a realização da dupla conferência.

        Para cada unidade coletada, notifica o evento 'dupla_conferencia' aos observadores do robô antes de adicioná-la à bandeja.

        Args:
            robo: Instância do robô que executa a coleta.
            item: Codinome do item a ser coletado.
            quantidade: Quantidade de unidades a coletar. Padrão é 1.
        """
        for _ in range(quantidade):
            robo.notificar("dupla_conferencia", item=item)
            robo.coletar(item)
