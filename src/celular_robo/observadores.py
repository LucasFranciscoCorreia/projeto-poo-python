# Observer — EquipeDeTestes, RegistroAuditoria — enunciado, Seção 2.3.
#
# Herde de `Observador` (observadores_base.py — ABC com registro automático):
#
#   from celular_robo.observadores_base import Observador
#
# TODO: implemente aqui. EquipeDeTestes(Observador) reage a "bandeja_pronta";
# RegistroAuditoria(Observador) loga todo evento (coleta, bandeja pronta,
# pedido rejeitado), pensando em trilha de auditoria, não só depuração.

from src.celular_robo.observadores_base import Observador

class EquipeDeTestes(Observador):
    def notificar(self, evento, robo):
        if evento == "bandeja_pronta":
            ...

class RegistroAuditoria(Observador):
    def notificar(self, evento, robo):
        print(f"Registro de Auditoria: evento '{evento}' do robô {robo}")
