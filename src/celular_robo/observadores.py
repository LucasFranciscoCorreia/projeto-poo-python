# Observer — EquipeDeTestes, RegistroAuditoria — enunciado, Seção 2.3.
#
# Herde de `Observador` (observadores_base.py — ABC com registro automático):
#
#   from celular_robo.observadores_base import Observador
#
# TODO: implemente aqui. EquipeDeTestes(Observador) reage a "bandeja_pronta";
# RegistroAuditoria(Observador) loga todo evento (coleta, bandeja pronta,
# pedido rejeitado), pensando em trilha de auditoria, não só depuração.

from datetime import datetime, timezone

from celular_robo.modos import ModoAguardandoVerificacao, ModoColetando
from celular_robo.observadores_base import Observador
from celular_robo.robo_base import Robo


class EquipeDeTestes(Observador):
    def __init__(self) -> None:
        super().__init__()
        self.notificacoes: list[dict[str, str | datetime]] = []
        self.ultimo_status = None

    def atualizar(self, evento: str, **kwargs):
        if evento == "bandeja_pronta":
            self.notificacoes.append(
                {"timestamp": datetime.now(timezone.utc), "dados": kwargs}
            )

    def aprovar(self, robo: Robo):
        self.ultimo_status: str = "aprovado"
        if hasattr(robo, "bandeja"):
            robo.bandeja.itens = {}
        robo.notificar("lote_aprovado", status="aprovado")

    def rejeitar(self, robo: Robo):
        self.ultimo_status: str = "rejeitado"
        robo.notificar("lote_rejeitado", status="rejeitado")


class RegistroAuditoria(Observador):
    def __init__(self) -> None:
        super().__init__()
        self._registros: list[dict[str, str | datetime]] = []

    def atualizar(self, evento: str, **kwargs):
        log = {
            "evento": evento,
            "timestamp": datetime.now(timezone.utc),
            "msg": kwargs
        }

        self._registros.append(log)

    def __len__(self) -> int:
        return len(self._registros)

    @property
    def registros(self) -> list[dict[str, str | datetime]]:
        registros: list[dict[str, str | datetime]] = []
        for data in self._registros:
            registros.append(dict(data))
        return registros


class MonitorBandeja(Observador):
    def atualizar(self, evento: str, **kwargs):
        if evento == "bandeja_pronta":
            robo = kwargs["robo"]
            robo.modo = ModoAguardandoVerificacao()
        elif evento in ("lote_aprovado", "lote_rejeitado"):
            robo = kwargs["robo"]
            robo.modo = ModoColetando()
