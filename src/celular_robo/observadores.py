# Observer — EquipeDeTestes, RegistroAuditoria — enunciado, Seção 2.3.
#
# Herde de `Observador` (observadores_base.py — ABC com registro automático):
#
#   from celular_robo.observadores_base import Observador
#
# TODO: implemente aqui. EquipeDeTestes(Observador) reage a "bandeja_pronta";
# RegistroAuditoria(Observador) loga todo evento (coleta, bandeja pronta,
# pedido rejeitado), pensando em trilha de auditoria, não só depuração.

from celular_robo.modos import ModoColetando
from celular_robo.modos import ModoAguardandoVerificacao
from datetime import datetime

from celular_robo.observadores_base import Observador

class EquipeDeTestes(Observador):
    def __init__(self) -> None:
        super().__init__()
        self.notificacoes = []
        self.ultimo_status = None

    def atualizar(self, evento, **kwargs):
        if evento == "bandeja_pronta":
            self.notificacoes.append(
                {"timestamp": datetime.now(), "dados": kwargs}
            )

    def aprovar(self, robo):
        self.ultimo_status = "aprovado"
        if hasattr(robo, "bandeja"):
            robo.bandeja.itens = {}
        robo.notificar("lote_aprovado", status="aprovado")

    def rejeitar(self, robo):
        self.ultimo_status = "rejeitado"
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
        
        self._registros.append(log)

    def __len__(self):
        return len(self._registros)

    @property
    def registros(self):
        registros = []
        for data in self._registros:
            registros.append(dict(data))
        return registros

class MonitorBandeja(Observador):
    def atualizar(self, evento, **kwargs):
        if evento == "bandeja_pronta":
            robo = kwargs["robo"]
            robo.modo = ModoAguardandoVerificacao()
        elif evento in ("lote_aprovado", "lote_rejeitado"):
            robo = kwargs["robo"]
            robo.modo = ModoColetando()