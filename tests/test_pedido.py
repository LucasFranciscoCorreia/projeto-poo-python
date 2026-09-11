# TODO: seus testes de pedido — enunciado, Seção 2.7 (pytest.raises(PedidoInvalido),
# conflito fragil+urgente de Seção 2.4).

import json
import pytest

from celular_robo.comandos import ComandoColeta
from celular_robo.excecoes import PedidoInvalido
from celular_robo.persistencia import montar_pedido_de_json


def test_arquivo_inexistente_ou_json_invalido(tmp_path):
    with pytest.raises(PedidoInvalido):
        montar_pedido_de_json("caminho_inexistente.json")

    arquivo_corrompido = tmp_path / "corrompido.json"
    arquivo_corrompido.write_text("{json_invalido", encoding="utf-8")
    with pytest.raises(PedidoInvalido):
        montar_pedido_de_json(str(arquivo_corrompido))


def test_pedido_vazio_ou_sem_itens(tmp_path):
    arquivo_vazio = tmp_path / "vazio.json"
    arquivo_vazio.write_text(json.dumps({"lote": "Lote Vazio", "itens": []}), encoding="utf-8")

    with pytest.raises(PedidoInvalido):
        montar_pedido_de_json(str(arquivo_vazio))


def test_pedido_com_campos_invalidos(tmp_path):

    arq_qtd = tmp_path / "qtd_invalida.json"
    arq_qtd.write_text(json.dumps({
        "itens": [{"codinome": "Projeto Aurora", "quantidade": 0, "posicao": [1, 1]}]
    }), encoding="utf-8")
    with pytest.raises(PedidoInvalido):
        montar_pedido_de_json(str(arq_qtd))

    arq_pos = tmp_path / "pos_invalida.json"
    arq_pos.write_text(json.dumps({
        "itens": [{"codinome": "Projeto Aurora", "quantidade": 1, "posicao": [1]}]
    }), encoding="utf-8")
    with pytest.raises(PedidoInvalido):
        montar_pedido_de_json(str(arq_pos))


def test_conflito_item_fragil_e_urgente_no_mesmo_item(tmp_path):
    arquivo = tmp_path / "item_conflitante.json"
    arquivo.write_text(json.dumps({
        "itens": [
            {"codinome": "Projeto Aurora", "quantidade": 1, "posicao": [2, 2], "fragil": True, "urgente": True}
        ]
    }), encoding="utf-8")

    with pytest.raises(PedidoInvalido, match="contraditório"):
        montar_pedido_de_json(str(arquivo))


def test_conflito_itens_mistos_fragil_e_urgente_no_mesmo_pedido():
    with pytest.raises(PedidoInvalido, match="misturar itens frágeis e urgentes"):
        montar_pedido_de_json("dados/pedido_coleta_invalido.json")


def test_carregar_pedido_valido_sucesso():
    comandos = montar_pedido_de_json("dados/pedido_coleta_exemplo.json")
    assert len(comandos) == 2
    assert all(isinstance(c, ComandoColeta) for c in comandos)
    assert comandos[0].codinome == "Projeto Aurora"
    assert comandos[0].posicao == (3, 4)
    assert comandos[0].quantidade == 2
    assert comandos[1].codinome == "Projeto Vesper"
    assert comandos[1].posicao == (7, 2)
    assert comandos[1].quantidade == 1
