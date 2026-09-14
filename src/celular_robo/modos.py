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
    """
    Estado de operação padrão em que o robô está ativo e apto a coletar.
    
    Permite a movimentação livre pelo laboratório delegando o deslocamento para a estratégia de rota atualmente configurada no robô.
    """
    def mover(self, robo: Robo):
        """
        Move o robô de acordo com a sua estratégia de navegação.
        
        Args:
            robo: Instância do robô em operação.
        
        Returns:
            True se a movimentação foi bem-sucedida; False caso contrário.
        """
        return robo.estrategia.mover(robo)


class ModoAguardandoVerificacao(ModoOperacao):
    """
    Estado de espera e bloqueio operacional do robô.
    
    Ativado quando a bandeja de coleta está cheia ou concluída, impedindo qualquer movimentação ou nova coleta até que a equipe de testes aprove ou rejeite o lote na bancada de verificação.
    """
    def mover(self, robo: Robo):
        """
        Bloqueia a movimentação do robô enquanto aguarda liberação.
        
        Exibe mensagem informativa no console alertando sobre o bloqueio e impede o deslocamento físico do robô.

        Args:
            robo: Instância do robô que tentou se movimentar.
        
        Returns:
            Sempre False, indicando que a movimentação não pôde ser realizada.
        """
        print(f"{robo.nome} está aguardando verificação da equipe de testes. Movimentação bloqueada.")
        return False
