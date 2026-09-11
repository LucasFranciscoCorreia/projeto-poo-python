# State — ModoColetando, ModoAguardandoVerificacao — enunciado, Seção 2.3.
#
# Herde de `ModoOperacao` (modos_base.py — ABC com registro automático):
#
#   from celular_robo.modos_base import ModoOperacao
#
# TODO: implemente aqui. A transição ModoColetando -> ModoAguardandoVerificacao
# acontece via Observer (não é o próprio modo que decide sozinho), quando a
# bandeja completa.

from celular_robo.modos_base import ModoOperacao
from celular_robo.robo_base import Robo


class ModoColetando(ModoOperacao):
    def mover(self, robo: Robo):
        return robo.estrategia.mover(robo)


class ModoAguardandoVerificacao(ModoOperacao):
    def mover(self, robo: Robo):
        print(f"{robo.nome} está aguardando verificação da equipe de testes. Movimentação bloqueada.")
        return False
