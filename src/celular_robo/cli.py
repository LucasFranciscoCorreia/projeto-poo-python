# CLI — enunciado, Seção 4.
#
# TODO: implemente aqui. Menu interativo (ou argparse, à sua escolha):
# listar pedido carregado, processar pedido, ver estado da bandeja,
# aprovar/rejeitar retirada da equipe de testes.

import json
from datetime import datetime

from celular_robo.comandos import ComandoColeta
from celular_robo.excecoes import ConfiguracaoInvalida, ErroColeta, PedidoInvalido
from celular_robo.modos import ModoAguardandoVerificacao
from celular_robo.observadores import (
    DespachanteTransporte,
    EquipeDeTestes,
    MonitorBandeja,
    Observador,
    RegistroAuditoria,
)
from celular_robo.persistencia import montar_pedido_de_json, montar_robo_de_config
from celular_robo.robo_base import Robo


class CLIApp:
    """
    Interface interativa no terminal para testar o robô e os pedidos.
    """
    def __init__(self):
        self.robo: Robo = None
        self.equipe: Observador = EquipeDeTestes()
        self.monitor: Observador = MonitorBandeja()
        self.auditoria: Observador = RegistroAuditoria()
        self.despachante: Observador = DespachanteTransporte()
        self.pedidos_comandos: list[ComandoColeta] = []
        self.caminho_pedido_atual: str | None = None

    def carregar_robo(self) -> None:
        """
        Carrega a configuração do robô a partir do arquivo JSON.
        """
        padrao: str = "dados/config_robo_exemplo.json"
        caminho: str = input(f"Caminho da config do robô [{padrao}]: ").strip() or padrao
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                config: dict[str, str] = json.load(f)
            self.robo: Robo = montar_robo_de_config(config, observadores=[self.equipe, self.monitor, self.auditoria, self.despachante])
            if self.pedidos_comandos:
                self.robo.definir_pedido(self.pedidos_comandos)

            print(f"\n[OK] Robô '{self.robo.nome}' configurado com sucesso!")
            print(f"     Estratégia: {self.robo.estrategia.identificador} | Modo: {self.robo.modo.__class__.__name__}")
            print(f"     Posição inicial: ({self.robo.x}, {self.robo.y}) | Obstáculos: {len(self.robo.obstaculos)}")
        except FileNotFoundError:
            print(f"\n[ERRO] Arquivo não encontrado: {caminho}")
        except json.JSONDecodeError as e:
            print(f"\n[ERRO] JSON inválido: {e}")
        except ConfiguracaoInvalida as e:
            print(f"\n[ERRO DE CONFIGURAÇÃO] {e}")

    def carregar_pedido(self) -> None:
        """
        Carrega um pedido a partir de um arquivo JSON e carrega os comandos de coleta.
        """
        padrao: str = "dados/pedido_coleta_exemplo.json"
        caminho: str = input(f"Caminho do arquivo de pedido [{padrao}]: ").strip() or padrao
        try:
            comandos: list[ComandoColeta] = montar_pedido_de_json(caminho)
            self.pedidos_comandos: list[ComandoColeta] = comandos
            self.caminho_pedido_atual: str = caminho

            if self.robo is not None:
                self.robo.definir_pedido(self.pedidos_comandos)

            print(f"\n[OK] Pedido carregado com sucesso! Total de itens: {len(comandos)}")
            self.listar_pedido()
        except PedidoInvalido as e:
            print(f"\n[ERRO DE PEDIDO] {e}")

    def listar_pedido(self) -> None:
        """
        Exibe no terminal a listagem de todos os itens e posições do pedido.
        """
        if not self.pedidos_comandos:
            print("\nNenhum pedido carregado no momento.")
            return
        print(f"\n--- Itens do Pedido ({self.caminho_pedido_atual}) ---")
        for i, cmd in enumerate(self.pedidos_comandos, 1):
            flag_fragil: str = " [FRÁGIL]" if cmd.fragil else ""
            flag_urgente: str = " [URGENTE]" if cmd.urgente else ""
            print(f"  {i}. {cmd.codinome} | Quantidade: {cmd.quantidade} | Posição: {cmd.posicao}{flag_fragil}{flag_urgente}")
        print("-------------------------------------------------")

    def processar_pedido(self) -> None:
        """
        Executa sequencialmente os comandos de coleta com o robô ativo.
        """
        if self.robo is None:
            print("\n[AVISO] Configure um robô primeiro (Opção 1).")
            return
        if not self.pedidos_comandos:
            print("\n[AVISO] Carregue um pedido primeiro (Opção 2).")
            return
        if isinstance(self.robo.modo, ModoAguardandoVerificacao):
            print(f"\n[BLOQUEADO] O robô '{self.robo.nome}' está em 'ModoAguardandoVerificacao'.")
            print("A equipe de testes precisa aprovar (Opção 6) ou rejeitar (Opção 7) o lote anterior antes de iniciar nova coleta.")
            return

        if self.robo.pedido_completo:
            print("\n[AVISO] Todos os itens deste pedido já foram coletados e estão na bandeja.")
            print("Conforme a Seção 2.3 do enunciado, os itens já coletados não precisam ser reprocessados.")
            return

        print(f"\nIniciando coleta com o robô '{self.robo.nome}'...")
        try:
            for cmd in self.pedidos_comandos:
                print(f" -> Navegando até {cmd.posicao} para coletar {cmd.quantidade}x '{cmd.codinome}'...")
                cmd.executar(self.robo)

            self.robo.notificar("bandeja_pronta")
            print("\n[SUCESSO] Todos os itens foram coletados!")
            print(f"O robô entrou em '{self.robo.modo.__class__.__name__}' aguardando liberação da bancada.")
        except (ErroColeta, ValueError) as e:
            print(f"\n[FALHA NA COLETA] {e}")

    def ver_estado_bandeja(self) -> None:
        """
        Exibe a telemetria do robô, bateria, coordenadas e itens na bandeja.
        """
        if self.robo is None:
            print("\n[AVISO] Nenhum robô configurado no momento.")
            return

        print(f"\n--- Estado do Robô: {self.robo.nome} ---")
        print(f"  Posição atual: ({self.robo.x}, {self.robo.y}) | Direção: {self.robo.direcao.name}")
        print(f"  Modo de operação: {self.robo.modo.__class__.__name__}")
        print(f"  Bateria: {self.robo.bateria}%")
        print(f"  Total de aparelhos na bandeja: {len(self.robo.bandeja)}")
        if self.robo.bandeja.itens:
            for item, qtd in self.robo.bandeja.itens.items():
                print(f"    - {item}: {qtd} unidade(s)")
        else:
            print("    (Bandeja vazia)")
        print("----------------------------------------")

    def aprovar_retirada(self) -> None:
        """
        Simula a aprovação do lote pela equipe de testes, esvaziando a bandeja.
        """
        if self.robo is None:
            print("\n[AVISO] Nenhum robô configurado.")
            return
        self.equipe.aprovar(self.robo)
        print("\n[EQUIPE DE TESTES] Lote APROVADO!")
        print(f"A bandeja foi esvaziada e o robô retornou para '{self.robo.modo.__class__.__name__}'.")
        if getattr(self.despachante, "ultimo_transporte_sucesso", False) and getattr(self.despachante, "transportador", None):
            t = self.despachante.transportador
            print(f"[TRANSPORTE] {t.nome} assumiu o lote e entregou no ponto de retirada ({t.x}, {t.y}) com sucesso!")

    def rejeitar_retirada(self) -> None:
        """
        Simula a rejeição do lote pela equipe de testes, mantendo os itens na bandeja.
        """
        if self.robo is None:
            print("\n[AVISO] Nenhum robô configurado.")
            return
        self.equipe.rejeitar(self.robo)
        print("\n[EQUIPE DE TESTES] Lote REJEITADO!")
        print(f"Os itens permanecem na bandeja para averiguação. Robô em '{self.robo.modo.__class__.__name__}'.")

    def exibir_auditoria(self) -> None:
        """
        Imprime a trilha de auditoria com timestamp e eventos registrados.
        """
        registros: list[dict[str, str | datetime]] = self.auditoria.registros
        if not registros:
            print("\nTrilha de auditoria vazia.")
            return
        print(f"\n--- Trilha de Auditoria ({len(registros)} registros) ---")
        for reg in registros:
            ts = reg["timestamp"].strftime("%H:%M:%S")
            evento = reg["evento"]
            msg = {k: v for k, v in reg["msg"].items() if k != "robo"}
            print(f"  [{ts}] Evento: {evento:<18} | Detalhes: {msg}")
        print("-----------------------------------------------------")

    def executar(self) -> None:
        """
        Executa o laço principal do menu interativo no terminal.
        """
        while True:
            print("\n=========================================")
            print("   Laboratório de Coleta de Celulares")
            print("=========================================")
            print(" 1. Carregar configuração do robô")
            print(" 2. Carregar pedido de coleta")
            print(" 3. Listar pedido carregado")
            print(" 4. Processar pedido (executar coleta)")
            print(" 5. Ver estado da bandeja e do robô")
            print(" 6. Aprovar lote (Equipe de Testes)")
            print(" 7. Rejeitar lote (Equipe de Testes)")
            print(" 8. Exibir trilha de auditoria")
            print(" 0. Sair")
            print("=========================================")
            opcao = input("Selecione uma opção: ").strip()

            if opcao == "1":
                self.carregar_robo()
            elif opcao == "2":
                self.carregar_pedido()
            elif opcao == "3":
                self.listar_pedido()
            elif opcao == "4":
                self.processar_pedido()
            elif opcao == "5":
                self.ver_estado_bandeja()
            elif opcao == "6":
                self.aprovar_retirada()
            elif opcao == "7":
                self.rejeitar_retirada()
            elif opcao == "8":
                self.exibir_auditoria()
            elif opcao == "0":
                print("\nEncerrando sistema. Até logo!\n")
                break
            else:
                print("\nOpção inválida, tente novamente.")


def main() -> None:
    app = CLIApp()
    app.executar()


if __name__ == "__main__":
    main()
