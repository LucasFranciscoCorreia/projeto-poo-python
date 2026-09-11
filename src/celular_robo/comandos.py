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
from celular_robo.estrategias import RotaColeta
from celular_robo.excecoes import ErroColeta
from celular_robo.modos import ModoAguardandoVerificacao
from celular_robo.robo_base import Robo


class ComandoColeta(Comando):
    def __init__(self, codinome: str, posicao: tuple[int, int], quantidade: int, fragil: bool = False, urgente: bool = False):
        super().__init__()
        self.codinome: str = codinome
        self.posicao: tuple[int, int] = tuple(posicao)
        self.quantidade: int = quantidade
        self.fragil: bool = fragil
        self.urgente: bool = urgente

    def executar(self, robo: Robo) -> None:
        if isinstance(robo.modo, ModoAguardandoVerificacao):
            raise ErroColeta(
                f"{robo.nome} está aguardando verificação da bancada e não pode iniciar nova coleta."
            )

        qtd_atual: int = robo.bandeja.itens.get(self.codinome, 0)
        limite: int | None = robo.bandeja.limite_itens.get(self.codinome)
        if limite is not None and qtd_atual >= limite:
            return

        if isinstance(robo.estrategia, RotaColeta):
            chegou: bool = robo.estrategia.mover(robo, destino=self.posicao)
        else:
            chegou: bool = robo.estrategia.mover(robo)

        if not chegou or (robo.x, robo.y) != self.posicao:
            raise ErroColeta(
                f"Robô '{robo.nome}' não conseguiu alcançar a posição {self.posicao} "
                f"do item '{self.codinome}' (parou em ({robo.x}, {robo.y}) devido a obstáculo ou limite do laboratório)."
            )

        qtd_a_coletar: int = self.quantidade if limite is None else min(self.quantidade, limite - qtd_atual)
        robo.estrategia.coletar(robo, self.codinome, qtd_a_coletar)

    def desfazer(self, robo: Robo) -> None:
        for _ in range(self.quantidade):
            robo.remover(self.codinome)
