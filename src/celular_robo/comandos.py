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
from celular_robo.excecoes import ErroColeta
from celular_robo.modos import ModoAguardandoVerificacao


class ComandoColeta(Comando):
    def __init__(self, codinome, posicao, quantidade, fragil=False, urgente=False):
        super().__init__()
        self.codinome = codinome
        self.posicao = tuple(posicao)
        self.quantidade = quantidade
        self.fragil = fragil
        self.urgente = urgente

    def executar(self, robo):
        if isinstance(robo.modo, ModoAguardandoVerificacao):
            raise ErroColeta(
                f"{robo.nome} está aguardando verificação da bancada e não pode iniciar nova coleta."
            )

        qtd_atual = robo.bandeja.itens.get(self.codinome, 0)
        limite = robo.bandeja.limite_itens.get(self.codinome, None)
        if limite is not None and qtd_atual >= limite:
            return

        try:
            chegou = robo.estrategia.mover(robo, destino=self.posicao)
        except TypeError:
            chegou = robo.estrategia.mover(robo)

        if not chegou or (robo.x, robo.y) != self.posicao:
            raise ErroColeta(
                f"Robô '{robo.nome}' não conseguiu alcançar a posição {self.posicao} "
                f"do item '{self.codinome}' (parou em ({robo.x}, {robo.y}) devido a obstáculo ou limite do laboratório)."
            )

        qtd_a_coletar = self.quantidade if limite is None else min(self.quantidade, limite - qtd_atual)
        robo.estrategia.coletar(robo, self.codinome, qtd_a_coletar)

    def desfazer(self, robo):
        for _ in range(self.quantidade):
            robo.remover(self.codinome)
