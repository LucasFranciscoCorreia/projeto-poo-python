# Configuração e persistência — enunciado, Seção 2.6.
#
# TODO: implemente aqui. montar_robo_de_config(config) e
# montar_pedido_de_json(caminho) — mesmo par de funções do capstone do curso
# (montar_robo_de_config/montar_frota_de_json), adaptado: um arquivo
# configura o robô (tipo, estratégia, área), outro traz o pedido de coleta.

import json

from celular_robo.comandos import ComandoColeta
from celular_robo.excecoes import PedidoInvalido
from celular_robo.fabrica import criar_robo_configurado
from celular_robo.robo_base import Robo


def montar_robo_de_config(config: dict[str, str], **kwargs) -> Robo:
    tipo_nome = config.get("tipo_nome", "RoboColetor")
    nome = config.get("nome", "Coletor-1")
    estrategia_nome = config.get("estrategia_nome", "direta")
    area_nome = config.get("area_nome", "centro_padrao")

    return criar_robo_configurado(tipo_nome, nome, estrategia_nome=estrategia_nome, area_nome=area_nome, **kwargs)


def montar_pedido_de_json(caminho: str) -> list[ComandoColeta]:
    try:
        with open(caminho, 'r', encoding='utf-8') as file:
            pedido = json.load(file)
    except FileNotFoundError:
        raise PedidoInvalido(f"Arquivo de pedido não encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise PedidoInvalido(f"Formato JSON invalido no arquivo {caminho}: {e}")

    itens: list[dict[str, str | int | list[int, int] | bool]] = pedido.get("itens")

    if not itens:
        raise PedidoInvalido("O pedido de coleta não pode ser vazio ou sem itens.")

    for item in itens:
        if item.get("fragil", False) and item.get("urgente", False):
            raise PedidoInvalido(f"Item {item.get('codinome')!r} contraditório: não pode ser 'fragil' e 'urgente' ao mesmo tempo.")

    tem_fragil = any(item.get("fragil", False) for item in itens)
    tem_urgente = any(item.get("urgente", False) for item in itens)

    if tem_fragil and tem_urgente:
        raise PedidoInvalido("Não é possível misturar itens frágeis e urgentes no mesmo pedido.")

    comandos = []
    for item in itens:
        codinome = item.get("codinome")
        quantidade = item.get("quantidade")
        posicao = item.get("posicao")
        fragil = item.get("fragil", False)
        urgente = item.get("urgente", False)

        if not codinome or not isinstance(codinome, str):
            raise PedidoInvalido(f"Item com codinome inválido: {codinome!r}")

        if not isinstance(quantidade, int) or quantidade <= 0:
            raise PedidoInvalido(f"Quantidade inválida para o item {codinome!r}: {quantidade}")

        if not posicao or len(posicao) != 2:
            raise PedidoInvalido(f"Posição inválida para o item {codinome!r}: {posicao}")

        if fragil and urgente:
            raise PedidoInvalido(f"Item {codinome!r} contraditório: não pode ser 'fragil' e 'urgente' ao mesmo tempo.")
        comandos.append(ComandoColeta(codinome=codinome, posicao=posicao, quantidade=quantidade, fragil=fragil, urgente=urgente))
    return comandos
