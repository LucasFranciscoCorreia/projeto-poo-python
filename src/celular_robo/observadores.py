# Observer — EquipeDeTestes, RegistroAuditoria — enunciado, Seção 2.3.
#
# Herde de `Observador` (observadores_base.py — ABC com registro automático):
#
#   from celular_robo.observadores_base import Observador
#
# TODO: implemente aqui. EquipeDeTestes(Observador) reage a "bandeja_pronta";
# RegistroAuditoria(Observador) loga todo evento (coleta, bandeja pronta,
# pedido rejeitado), pensando em trilha de auditoria, não só depuração.

from datetime import datetime

from src.celular_robo.observadores_base import Observador

class EquipeDeTestes(Observador):
    def __init__(self) -> None:
        super().__init__()
        self.notificacoes = []

    def atualizar(self, evento, **kwargs):
        if evento == "bandeja_pronta":
            self.notificacoes.append(
                {"timestamp": datetime.now(), "dados": kwargs}
            )

    def aprovar(self, robo):
        robo.notificar("lote_aprovado", status="aprovado")

    def rejeitar(self, robo):
        robo.notificar("lote_rejeitado", status="rejeitado")


class RegistroAuditoria(Observador):
    def __init__(self) -> None:
        super().__init__()
        self._registros = []

    def atualizar(self, evento, **kwargs):
        log = {
            "evento": evento,
            "timestamp": datetime.now(),
            "msg": kwargs
        }
        print(log)
        self._registros.append(log)

    def __len__(self):
        return len(self._registros)

    @property
    def registros(self):
        return dict(self._registros)