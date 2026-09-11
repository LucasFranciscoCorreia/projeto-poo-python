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
    _registro: ClassVar[dict[str, type[RotaColeta]]] = {}

    def __init_subclass__(cls, identificador: str | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        chave: str = identificador or cls.__name__
        cls.identificador: str = chave
        RotaColeta._registro[chave] = cls

    def mover(self, robo: Robo, destino: tuple[int, int] | None = None) -> bool:
        if destino:
            return self._deslocar_ate(robo, destino)
        else:
            return robo.avancar()

    def _deslocar_ate(self, robo: Robo, destino: tuple[int, int]) -> bool:
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
        ...


class RotaDireta(RotaColeta, identificador="direta"):
    def coletar(self, robo: Robo, item: str, quantidade: int = 1):
        for _ in range(quantidade):
            robo.coletar(item)


class RotaComDuplaConferencia(RotaColeta, identificador="dupla_conferencia"):
    def coletar(self, robo: Robo, item: str, quantidade: int = 1):
        for _ in range(quantidade):
            robo.notificar("dupla_conferencia", item=item)
            robo.coletar(item)
