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
    """
    Observador que simula a bancada de verificação e controle de qualidade.
    
    Escuta avisos de conclusão de bandeja e fornece métodos para que a equipe aprove ou rejeite o lote inspecionado, notificando o robô sobre a decisão.
    
    Attributes:
        notificacoes: Histórico de avisos recebidos com timestamp UTC e dados do evento.
        ultimo_status: Última decisão tomada pela equipe ('aprovado', 'rejeitado' ou None).
    """
    def __init__(self) -> None:
        super().__init__()
        self.notificacoes: list[dict[str, str | datetime]] = []
        self.ultimo_status = None

    def atualizar(self, evento: str, **kwargs) -> None:
        """
        Recebe notificações emitidas pelos robôs observados.
        
        Args:
            evento: Nome do evento disparado (ex.: 'bandeja_pronta').
            **kwargs: Metadados associados ao evento.
        """
        if evento == "bandeja_pronta":
            self.notificacoes.append(
                {"timestamp": datetime.now(timezone.utc), "dados": kwargs}
            )

    def aprovar(self, robo: Robo) -> None:
        """
        Aprova o lote inspecionado, esvazia a bandeja e notifica o robô.
        
        Args:
            robo: Instância do robô cujo lote foi aprovado.
        """
        self.ultimo_status: str = "aprovado"
        if hasattr(robo, "bandeja"):
            robo.bandeja.itens = {}
        robo.notificar("lote_aprovado", status="aprovado")

    def rejeitar(self, robo: Robo) -> None:
        """
        Rejeita o lote inspecionado mantendo os itens na bandeja e notifica o robô.
        
        Args:
            robo: Instância do robô cujo lote foi rejeitado.
        """
        self.ultimo_status: str = "rejeitado"
        robo.notificar("lote_rejeitado", status="rejeitado")


class RegistroAuditoria(Observador):
    """
    Observador responsável por salvar o histórico de eventos do robô com timestamp UTC para depuração.
    
    Attributes:
        _registros: Lista interna de registros contendo evento, timestamp e metadados.
        registros: Propriedade pública que retorna cópias dos registros para evitar modificação externa.
    """

    def __init__(self) -> None:
        super().__init__()
        self._registros: list[dict[str, str | datetime]] = []

    def atualizar(self, evento: str, **kwargs) -> None:
        """
        Registra um evento com timestamp UTC e metadados na trilha de auditoria.
        
        Args:
            evento: Nome do evento capturado.
            **kwargs: Parâmetros e dados complementares da ocorrência.
        """
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
        """
        Lista de eventos registrados para auditoria.
        """
        registros: list[dict[str, str | datetime]] = []
        for data in self._registros:
            registros.append(dict(data))
        return registros


class MonitorBandeja(Observador):
    """
    Observador responsável por gerenciar a máquina de estados do robô.
    
    Reage às mudanças de preenchimento da bandeja e decisões da equipe de testes,  alternando o modo de operação do robô entre ativo e bloqueado para inspeção.
    """
    def atualizar(self, evento: str, **kwargs) -> None:
        """
        Atualiza o modo de operação do robô conforme os eventos recebidos.
        
        Coloca o robô em `ModoAguardandoVerificacao` ao receber 'bandeja_pronta', e restabelece o `ModoColetando` ao receber 'lote_aprovado' ou 'lote_rejeitado'.
        
        Args:
            evento: Nome do evento recebido.
            **kwargs: Dados do evento; deve conter a referência 'robo'.
        """
        if evento == "bandeja_pronta":
            robo = kwargs["robo"]
            robo.modo = ModoAguardandoVerificacao()
        elif evento in ("lote_aprovado", "lote_rejeitado"):
            robo = kwargs["robo"]
            robo.modo = ModoColetando()
