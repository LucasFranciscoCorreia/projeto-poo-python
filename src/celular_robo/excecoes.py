# Hierarquia de exceções — enunciado, Seção 2.5.
#
# TODO: implemente aqui. ErroColeta(Exception) como base;
# ConfiguracaoInvalida(ErroColeta) e PedidoInvalido(ErroColeta) como as duas
# subclasses (ver Seção 2.5 pra critério de qual usar em cada caso).

class ErroColeta(Exception):
    """
    Exceção base para todos os erros relacionados ao domínio de coleta.

    Pode ser capturada para tratar genericamente qualquer erro operacional do robô ou ser lançada diretamente em falhas durante a execução de coletas (por exemplo, quando o robô está em modo de verificação ou é bloqueado por obstáculos na rota).
    """
    pass


class ConfiguracaoInvalida(ErroColeta):
    """
    Exceção lançada quando uma configuração do robô é inválida ou inconsistente.

    Deve ser utilizada quando tipo, estratégia ou área forem inválidos, ou se a quarentena usar rota direta.
    """
    pass


class PedidoInvalido(ErroColeta):
    """
    Exceção lançada quando um pedido é considerado inválido ou inapropriado para o contexto atual.

    Deve ser utilizada se o JSON do pedido não existir, estiver quebrado, vazio ou misturar itens frágeis e urgentes.
    """
    pass
