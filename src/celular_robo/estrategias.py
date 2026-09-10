# Strategy — RotaDireta, RotaComDuplaConferencia — enunciado, Seção 2.3.
# (Não confundir com estrategias_base.py — genérico do curso, não editar. Ao
# contrário de Command/Observer/State, aqui você NÃO herda de `Estrategia`:
# escreva sua própria base, ver TODO abaixo — motivo em estrategias_base.py.)
#
# TODO: implemente aqui. Considere uma base comum (RotaColeta) com
# __init_subclass__ registrando cada rota, ver Seção 2.2 (metaprogramação
# aplicada a uma segunda hierarquia).

from celular_robo.robo_base import Direcao
from abc import ABC, abstractmethod


class RotaColeta(ABC):
    _registro = {}
    def __init_subclass__(cls, identificador=None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        chave = identificador or cls.__name__
        cls.identificador = chave
        RotaColeta._registro[chave] = cls

    def mover(self, robo, destino=None):
        if destino:
            self._deslocar_ate(robo, destino)
            return True
        else:
            return robo.avancar()
    
    def _deslocar_ate(self, robo, destino):
        """
        Navega pela grade até a coordenada de destino (x, y),
        girando e avançando respeitando os obstáculos.
        """
        alvo_x, alvo_y = destino
        while (robo.x, robo.y) != (alvo_x, alvo_y):
            # Ajuste no eixo X
            if robo.x < alvo_x:
                robo.girar_ate(Direcao.LESTE)
            elif robo.x > alvo_x:
                robo.girar_ate(Direcao.OESTE)
            # Ajuste no eixo Y
            elif robo.y < alvo_y:
                robo.girar_ate(Direcao.NORTE)
            elif robo.y > alvo_y:
                robo.girar_ate(Direcao.SUL)
            # Tenta avançar; se houver obstáculo, interrompe para não entrar em loop
            if not robo.avancar():
                break
    
    @abstractmethod
    def coletar(self, robo, item, quantidade=1):
        ...

class RotaDireta(RotaColeta, identificador="direta"):
    def coletar(self, robo, item, quantidade=1):
        for _ in range(quantidade):
            robo.coletar(item)
        

class RotaComDuplaConferencia(RotaColeta, identificador="dupla_conferencia"):
    def coletar(self, robo, item, quantidade=1):
        for _ in range(quantidade):
            robo.notificar("dupla_conferencia", item=item)
            robo.coletar(item)
