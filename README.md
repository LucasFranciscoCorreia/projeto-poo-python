# Robô Coletor de Celulares

Projeto Final da disciplina de Programação Orientada a Objetos em Python.
Implementação de um robô coletor de dispositivos móveis em laboratório de testes sobre grade com obstáculos, utilizando fundamentos avançados de Orientação a Objetos, Descriptors, Metaprogramação, 5 Padrões de Projeto (Strategy, Command, Factory, Observer, State), Linha de Produtos de Software (LPS) e persistência em JSON.

---

## Setup

O projeto requer **Python 3.10+** (testado com Python 3.14) e utiliza apenas a biblioteca padrão do Python, com exceção do `pytest` para a suíte de testes automatizados.

1. **Criação e ativação do ambiente virtual:**
   ```bash
   python -m venv .venv

   # No Windows (PowerShell):
   .venv\Scripts\Activate.ps1

   # No Linux/macOS:
   source .venv/bin/activate
   ```

2. **Instalação das dependências:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Como rodar

### 1. Suíte de Testes Automatizados (`pytest`)
O projeto conta com 25 testes cobrindo contratos, exceções, LPS, fluxos de estado, comandos e detecção de obstáculos:
```bash
pytest -v
```
*(O arquivo `pyproject.toml` configura `pythonpath = ["src"]`, permitindo a execução limpa direta da raiz do repositório).*

### 2. Interface de Linha de Comando (CLI)
Para iniciar a CLI interativa:
```bash
# No Windows (PowerShell):
$env:PYTHONPATH="src"; python -m celular_robo.cli

# No Linux/macOS:
PYTHONPATH=src python3 -m celular_robo.cli
```

A CLI permite carregar a configuração do robô, carregar pedidos, executar as coletas, inspecionar a bandeja, simular a aprovação/rejeição da equipe de testes e visualizar a trilha de auditoria.

---

## Decisões de projeto

1. **Modelagem da `Bandeja` e Descriptor `QuantidadeValida` (Seção 2.1)**:
   - Foi criado a classe dedicada `Bandeja`, encapsulando o dicionário de itens e implementando `__len__` (soma das unidades coletadas).
   - O descriptor `QuantidadeValida` gerencia o atributo `itens`, validando que as quantidades sejam inteiras, não-negativas e não ultrapassem as cotas do pedido (`limite_itens`).

2. **Conflito item a item — `fragil=True` e `urgente=True` no mesmo item (Seção 2.4)**:
   - Recusado com `PedidoInvalido` durante a validação em `montar_pedido_de_json`.

3. **Conflito entre itens distintos do mesmo pedido (Seção 2.4)**:
   - Se o pedido contiver ao menos um item `fragil=True` e ao menos um item `urgente=True`, o pedido inteiro é rejeitado na validação com `PedidoInvalido`.
   - O arquivo `dados/pedido_coleta_invalido.json` demonstra essa recusa, enquanto `dados/pedido_coleta_exemplo.json` traz um pedido válido.

4. **Tratamento de pedidos com itens inválidos (Seção 2.5)**:
   - Optou-se por rejeitar o pedido por completo com `PedidoInvalido` caso qualquer item contenha codinome inválido, quantidade não-positiva ou posição fora dos limites da grade, garantindo a atomicidade do lote de testes.

5. **Rejeição pela Equipe de Testes e Prevenção de Reprocessamento (Seções 1 e 2.3)**:
   - Quando a `EquipeDeTestes` rejeita a bandeja, o robô retorna para `ModoColetando`, mantendo os itens já coletados na bandeja (sem esvaziar).
   - O robô e o comando `ComandoColeta` impedem a duplicação de itens já coletados na bandeja, respeitando a regra de que itens coletados não precisam ser reprocessados.
   - O robô recusa novas coletas enquanto estiver em `ModoAguardandoVerificacao`.

6. **Hierarquia própria para `RotaColeta` (Seção 2.2)**:
   - Para não contaminar `Estrategia._registro` (que continha estratégias de movimentação genérica do curso), foi criada a base abstrata `RotaColeta(ABC)` com seu próprio `__init_subclass__`, derivando `ESTRATEGIAS_VALIDAS = set(RotaColeta._registro)`.

---

## Mapeamento pra aulas da disciplina

| Mecanismo / Conceito | Módulo / Arquivo | Classe / Símbolo | Descrição no Projeto |
|---|---|---|---|
| **Fundamentos de OO & Herança** | `src/celular_robo/robo.py` | `RoboColetor(Robo)` | Herda de `Robo`, reutiliza atributos de navegação e adiciona a `Bandeja` de coleta. |
| **Métodos Especiais (`__repr__`, `__len__`)** | `src/celular_robo/robo.py` | `RoboColetor`, `Bandeja` | `len(robo)` e `len(bandeja)` contam celulares; `__repr__` fornece representação formal. |
| **Descriptors** | `src/celular_robo/robo.py` | `QuantidadeValida` | Descriptor validando valores positivos e respeitando limites do pedido. |
| **Metaprogramação (`__init_subclass__`)** | `src/celular_robo/estrategias.py` | `RotaColeta._registro` | Registro automático de rotas de coleta (`RotaDireta`, `RotaComDuplaConferencia`). |
| **Strategy Pattern** | `src/celular_robo/estrategias.py` | `RotaDireta`, `RotaComDuplaConferencia` | Algoritmos intercambiáveis de rota (direta rápida vs. com revalidação). |
| **Command Pattern** | `src/celular_robo/comandos.py` | `ComandoColeta` | Encapsula a ação de coleta com métodos `.executar(robo)` e `.desfazer(robo)` (*undo* da bandeja). |
| **Factory Pattern** | `src/celular_robo/fabrica.py` | `criar_robo_configurado` | Valida configuração na LPS e instancia o robô via registro. |
| **Observer Pattern** | `src/celular_robo/observadores.py` | `EquipeDeTestes`, `RegistroAuditoria`, `MonitorBandeja` | Disparo de eventos (`"bandeja_pronta"`, `"lote_aprovado"`), transições e trilha de auditoria. |
| **State Pattern** | `src/celular_robo/modos.py` | `ModoColetando`, `ModoAguardandoVerificacao` | Estados do robô: operando coleta vs. bloqueado aguardando liberação da bancada. |
| **Linha de Produtos de Software (LPS)** | `src/celular_robo/modelo_features.py` | `validar_configuracao`, `REQUER`, `EXCLUI` | 4 dimensões com regras de inclusão/exclusão (ex.: quarentena exclui direta). |
| **Hierarquia de Exceções** | `src/celular_robo/excecoes.py` | `ErroColeta`, `ConfiguracaoInvalida`, `PedidoInvalido` | Exceções customizadas com herança para tratamento genérico ou granular. |
| **Persistência / Serialização** | `src/celular_robo/persistencia.py` | `montar_robo_de_config`, `montar_pedido_de_json` | Leitura de JSON para configuração do robô e montagem de comandos do lote. |
| **Testes Automatizados (`pytest`)** | `tests/` | 25 testes unitários e de integração | Cobertura total de contratos, parametrização, obstáculos e casos limites. |
| **Interface CLI** | `src/celular_robo/cli.py` | `CLIApp`, `main` | Menu interativo para operação completa do laboratório de testes. |
