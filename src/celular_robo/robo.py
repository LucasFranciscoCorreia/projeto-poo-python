# RoboColetor + QuantidadeValida — enunciado, Seção 2.1.
#
# `Robo` (posição, __init_subclass__/_registro, avancar/girar, estrategia/modo,
# Observer) já vem pronto em robo_base.py — não precisa reescrever, só importar:
#
#   from celular_robo.robo_base import Robo, Coordenada
#
# TODO: implemente aqui.
# - RoboColetor(Robo): reaproveita Coordenada (x, y) por herança — não precisa
#   redeclarar. Adicione o que for específico da coleta (ex.: bandeja).
# - QuantidadeValida: descriptor novo (mesmo protocolo de Coordenada/Percentual
#   em robo_base.py), validando que a quantidade coletada de um item nunca é
#   negativa nem passa do pedido.
# - __str__/__repr__ (robô) e __len__ (bandeja — quantos itens já coletados).

from celular_robo.modos import ModoColetando
from celular_robo.robo_base import Robo

class QuantidadeValida:
    def __set_name__(self, owner, name):
        self.nome_publico = name
        self.nome = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.setdefault(self.nome, {})

    def __set__(self, instance, valor):
        if not isinstance(valor, dict):
            raise ValueError(f"{self.nome_publico} deve ser um dicionário, recebi {type(valor).__name__}")
        
        for item, quantidade in valor.items():
            if not isinstance(quantidade, int):
                raise ValueError(f"{quantidade=} deve ser um inteiro")

            if quantidade < 0:
                raise ValueError(f"{self.nome_publico} não pode possuir valor negativo")

            if instance.limite_itens and item in instance.limite_itens and quantidade > instance.limite_itens[item]:
                raise ValueError(f"Quantidade de {item!r} ultrapassa o limite do pedido ({instance.limite_itens[item]})")
    
        instance.__dict__[self.nome] = dict(valor)

class Bandeja:
    itens = QuantidadeValida()
    def __init__(self, limite_itens=None):
        self.limite_itens = limite_itens or {}
        self.itens = {}

    def adicionar(self, item):
        novo = dict(self.itens)
        novo[item] = novo.get(item, 0) + 1
        self.itens = novo

    def remover(self, item):
        if item in self.itens:
            novo = dict(self.itens)
            novo[item] -= 1
            if novo[item] == 0:
                del novo[item]
            self.itens = novo

    def __len__(self):
        return sum(self.itens.values()) 

    @property
    def limite(self):
        return sum(self.limite_itens.values()) if self.limite_itens else 0


class RoboColetor(Robo):
    def __init__(self, nome, observadores = None, modo = None, **kwargs):
        modo = modo if modo is not None else ModoColetando()
        super().__init__(nome, modo=modo, **kwargs)
        if observadores is not None:
            for observador in observadores:
                self.adicionar_observador(observador)
        self.bandeja = Bandeja()

    def coletar(self, item):
        self.bandeja.adicionar(item)
        self.notificar("coleta", item=item)

    def remover(self, item):
        self.bandeja.remover(item)
        self.notificar("remocao", item=item)

    def __len__(self):
        return len(self.bandeja)

    def __repr__(self):
        return f"RoboColetor({super().__repr__()})"
