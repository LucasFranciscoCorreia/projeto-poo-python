# RoboColetor + QuantidadeValida — enunciado, Seção 2.1.
#
# `Robo` (posição, __init_subclass__/_registro, avancar/girar, estrategia/modo,
# Observer) já vem pronto em robo_base.py — não precisa reescrever, só
# importar:
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

from celular_robo.comandos import ComandoColeta
from celular_robo.excecoes import ErroColeta
from celular_robo.modos import ModoAguardandoVerificacao, ModoColetando
from celular_robo.modos_base import ModoOperacao
from celular_robo.observadores_base import Observador
from celular_robo.robo_base import Robo


class QuantidadeValida:
    """
    Descriptor para validação estrita das quantidades de itens na bandeja.
    
    Garante que os itens sejam armazenados em um dicionário onde cada chave mapeia para um inteiro não negativo que não ultrapasse a cota máxima estipulada no pedido.
    """
    def __set_name__(self, owner, name: str) -> None:
        self.nome_publico = name
        self.nome = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.setdefault(self.nome, {})

    def __set__(self, instance, valor: dict[str, int]) -> None:
        if not isinstance(valor, dict):
            raise TypeError(f"{self.nome_publico} deve ser um dicionário, recebi {type(valor).__name__}")
        
        for item, quantidade in valor.items():
            if not isinstance(quantidade, int):
                raise TypeError(f"{quantidade=} deve ser um inteiro")

            if quantidade < 0:
                raise ValueError(f"{self.nome_publico} não pode possuir valor negativo")

            if instance.limite_itens and item in instance.limite_itens and quantidade > instance.limite_itens[item]:
                raise ValueError(f"Quantidade de {item!r} ultrapassa o limite do pedido ({instance.limite_itens[item]})")
    
        instance.__dict__[self.nome] = dict(valor)


class Bandeja:
    """
    Representa a bandeja de armazenamento de itens coletados pelo robô.
    
    Utiliza o descriptor `QuantidadeValida` para proteger o estado interno e monitora as cotas de cada item configuradas no lote de coletas.
    
    Attributes:
        itens: Dicionário contendo as quantidades atualmente coletadas por item.
        limite_itens: Dicionário que mapeia o codinome do item para a cota máxima solicitada.
    """
    itens = QuantidadeValida()

    def __init__(self, limite_itens: dict[str, int] | None = None):
        """
        Inicializa a bandeja com os limites estipulados de cada item.
        
        Args:
            limite_itens: Dicionário com as cotas máximas para cada codinome de item.
        """
        self.limite_itens = limite_itens or {}
        self.itens: dict[str, int] = {}

    def adicionar(self, item: str) -> None:
        """
        Adiciona uma unidade do item especificado à bandeja.
        
        Args:
            item: Codinome do item a ser adicionado.
        """
        novo = dict(self.itens)
        novo[item] = novo.get(item, 0) + 1
        self.itens = novo

    def remover(self, item: str):
        """
        Remove uma unidade do item da bandeja.
        
        Args:
            item: Codinome do item a ser removido.
        """
        if item in self.itens:
            novo = dict(self.itens)
            novo[item] -= 1
            if novo[item] == 0:
                del novo[item]
            self.itens = novo

    def __len__(self) -> int:
        return sum(self.itens.values())

    @property
    def limite(self) -> int:
        """
        Soma total de todos os itens permitidos na bandeja.
        """
        return sum(self.limite_itens.values()) if self.limite_itens else 0


class RoboColetor(Robo):
    """
    Especialização do robô projetada para operações de coleta em laboratório.
    
    Incorpora uma bandeja interna de transporte, integra-se aos estados operacionais (ModoColetando e ModoAguardandoVerificacao) e emite eventos de ciclo de vida para observadores registrados.
    
    Attributes:
        bandeja: Instância de `Bandeja` responsável pelo estoque de itens coletados.
    """
    def __init__(self, nome: str, observadores: list[Observador] | None = None, modo: ModoOperacao | None = None, **kwargs):
        """
        Inicializa o robô coletor configurando observadores e modo inicial.
        
        Args:
            nome: Identificador textual único do robô.
            observadores: Lista inicial de observadores anexados ao robô.
            modo: Modo de operação inicial. Padrão é `ModoColetando`.
            **kwargs: Parâmetros adicionais repassados para a classe base `Robo`.
        """
        modo = modo if modo is not None else ModoColetando()
        super().__init__(nome, modo=modo, **kwargs)
        if observadores is not None:
            for observador in observadores:
                self.adicionar_observador(observador)
        self.bandeja: Bandeja = Bandeja()

    def definir_pedido(self, pedido_comandos: list[ComandoColeta]) -> None:
        """
        Configura as cotas da bandeja a partir de uma lista de comandos de pedido.
        
        Args:
            pedido_comandos: Lista de instâncias de `ComandoColeta` que formam o lote.
        """
        limites = {}
        for cmd in pedido_comandos:
            limites[cmd.codinome] = limites.get(cmd.codinome, 0) + cmd.quantidade
        self.bandeja.limite_itens = limites

    @property
    def pedido_completo(self) -> bool:
        """
        Indica se todas as cotas do pedido foram integralmente coletadas.
        """
        if not self.bandeja.limite_itens:
            return False
        return all(
            self.bandeja.itens.get(item, 0) >= limite
            for item, limite in self.bandeja.limite_itens.items()
        )

    def coletar(self, item: str) -> None:
        """
        Adiciona uma unidade do item à bandeja e notifica os observadores.
        
        Args:
            item: Codinome do item a ser coletado.
        
        Raises:
            ErroColeta: Se o robô estiver no estado `ModoAguardandoVerificacao`.
        """
        if isinstance(self.modo, ModoAguardandoVerificacao):
            raise ErroColeta(f"Robô '{self.nome}' está em ModoAguardandoVerificacao e recusa nova coleta.")
        self.bandeja.adicionar(item)
        self.notificar("coleta", item=item)

    def remover(self, item: str) -> None:
        """
        Remove uma unidade do item da bandeja e notifica os observadores.
        
        Args:
            item: Codinome do item a ser removido da bandeja.
        """
        self.bandeja.remover(item)
        self.notificar("remocao", item=item)

    def __len__(self) -> int:
        return len(self.bandeja)

    def __repr__(self) -> str:
        return f"RoboColetor({super().__repr__()})"
