# Command — ComandoColeta — enunciado, Seção 2.3.
#
# Herde de `Comando` (comandos_base.py — ABC com registro automático):
#
#   from celular_robo.comandos_base import Comando
#
# TODO: implemente aqui. ComandoColeta(Comando): __init__(codinome, posicao,
# quantidade), com .executar(robo) e .desfazer(robo) (remove o item da
# bandeja, decrementa a contagem coletada).

from celular_robo.comandos_base import Comando


class ComandoColeta(Comando):
    def __init__(self, codinome, posicao, quantidade, fragil=False, urgente=False):
        super().__init__()
        self.codinome = codinome
        self.posicao = tuple(posicao)
        self.quantidade = quantidade
        self.fragil = fragil
        self.urgente = urgente

    def executar(self, robo):
        robo.estrategia.mover(robo, destino=self.posicao)
        robo.estrategia.coletar(robo, self.codinome, self.quantidade)

    def desfazer(self, robo):
        for _ in range(self.quantidade):
            robo.remover(self.codinome)
