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

from src.celular_robo.robo_base import Robo

class QuantidadeValida:
    def __init__(self, maximo):
        self.maximo = maximo

    def __set_name__(self, owner, name):
        self.nome_publico = name
        self.nome = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.nome]

    def __set__(self, instance, valor):
        if not (0 <= valor <= self.maximo):
            raise ValueError(
                f"{self.nome_publico} não pode possuir valor negativo nem sair da quantidade máxima da bandeja"
                f"(0 a {self.maximo})"
            )
        instance.__dict__[self.nome] = valor

class Bandeja:
    quantidade = QuantidadeValida(10)
    def __init__(self):
        self.itens = {}
        self.quantidade = 0

    def adicionar(self, item):
        self.itens[item] = self.itens.get(item, 0) + 1
        self.quantidade += 1

    def remover(self, item):
        if item in self.itens:
            self.itens[item] -= 1
            self.quantidade -= 1
            if self.itens[item] <= 0:
                del self.itens[item]

    def __len__(self):
        return self.quantidade

class RoboColetor(Robo):
    def __init__(self, observadores = None, **kwargs):
        super().__init__(**kwargs)
        if observadores is not None:
            for observador in observadores:
                self.adicionar_observador(observador)
        self.bandeja = Bandeja()

    def coletar(self, item):
        self.bandeja.adicionar(item)
        for observador in self.observadores:
            observador.notificar("coleta", self)

    def remover(self, item):
        self.bandeja.remover(item)
        for observador in self.observadores:
            observador.notificar("remocao", self)

    def __len__(self):
        return len(self.bandeja)
