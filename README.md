# Robô Coletor de Celulares

Projeto final desenvolvido para a disciplina de Programação Orientada a Objetos em Python.

O sistema simula um robô coletor de dispositivos móveis operando em um laboratório com obstáculos sobre uma grade 2D. O foco do projeto foi aplicar na prática conceitos avançados de POO: Descriptors, Metaprogramação (`__init_subclass__`), 5 Padrões de Projeto (Strategy, Command, Factory, Observer, State), Linha de Produtos de Software (LPS) e persistência com JSON.

---

## Setup

O projeto utiliza Python 3.14 e apenas a biblioteca padrão, necessitando apenas do `pytest` para a execução dos testes automatizados.

1. **Criar e ativar o ambiente virtual:**
   ```bash
   python -m venv .venv

   # No Windows (PowerShell):
   .venv\Scripts\Activate.ps1

   # No Linux/macOS:
   source .venv/bin/activate
   ```

2. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Como rodar

### 1. Suíte de Testes Automatizados (`pytest`)
O projeto conta com 30 testes cobrindo contratos, exceções, LPS, fluxos de estado, comandos, detecção de obstáculos e a extensão opcional do robô transportador:
```bash
pytest -v
```
*(A raiz já conta com `pyproject.toml` configurado para apontar para a pasta `src/`).*

### 2. Interface de Linha de Comando (CLI)
Para abrir o menu interativo no terminal:
```bash
# No Windows (PowerShell):
$env:PYTHONPATH="src"; python -m celular_robo.cli

# No Linux/macOS:
PYTHONPATH=src python3 -m celular_robo.cli
```

Pelo menu é possível configurar o robô, carregar pedidos em JSON, rodar a coleta passo a passo, ver a bandeja e simular as aprovações/rejeições da equipe de testes.

---

## Decisões de projeto

Aqui estão as principais escolhas feitas durante o desenvolvimento:

1. #### Bandeja e Descriptor `QuantidadeValida` (Seção 2.1)
- Criei a classe `Bandeja` para encapsular o dicionário de itens e responder a `len(bandeja)` com o total de aparelhos.
- Usei o descriptor `QuantidadeValida` no atributo `itens` para garantir que o robô nunca armazene valores negativos nem colete além do limite estipulado no pedido.

2. #### Itens Conflitantes (`fragil` e `urgente` no mesmo item)
- Se um item tiver `fragil=True` e `urgente=True` ao mesmo tempo, a leitura do pedido recusa imediatamente levantando `PedidoInvalido`.

3. #### Conflito no Lote de Pedido (Seção 2.4)
- Um mesmo pedido não pode misturar itens frágeis e urgentes. Se isso ocorrer, optei por rejeitar o arquivo inteiro com PedidoInvalido (o arquivo dados/pedido_coleta_invalido.json demonstra essa recusa).

4. #### Validação Atômica de Pedidos (Seção 2.5)
- Preferi validar todos os campos do JSON antes de iniciar a operação (codinome válido, quantidade positiva e coordenadas na grade). Se qualquer item for inválido, o lote é rejeitado como um todo para evitar coletas parciais quebradas.

5. #### Rejeição pela Equipe de Testes e Evitar Reprocessamento
- Se a `EquipeDeTestes` rejeitar o lote, o robô retorna para `ModoColetando`, mas os itens continuam na bandeja.
- Tanto o robô quanto o comando `ComandoColeta` verificam o que já está na bandeja para não reprocessar coletas já feitas.
- Enquanto estiver em `ModoAguardandoVerificacao`, o robô recusa qualquer nova movimentação ou coleta.

6. #### Hierarquia Própria para `RotaColeta` (Seção 2.2)
- Para não misturar as estratégias deste trabalho com as estratégias genéricas de aula fornecidas em estrategias_base.py, criei uma base abstrata própria RotaColeta(ABC) com seu próprio __init_subclass__. Assim, ESTRATEGIAS_VALIDAS é derivada dinamicamente apenas das rotas deste domínio.

7. #### Extensão Opcional: RoboTransportador
- Criei a classe `RoboTransportador(Robo)` em `robo.py`, herdando diretamente de `Robo`. Por metaprogramação via `__init_subclass__`, a nova classe se registra automaticamente no dicionário `Robo._registro`, sem exigir nenhuma alteração na classe `RoboColetor`.
- A LPS reflete a novidade dinamicamente em `TIPOS_VALIDOS = set(Robo._registro)` e adiciona a restrição de domínio: `RoboTransportador` exclui `area_quarentena` (`EXCLUI["RoboTransportador"] = {"area_quarentena"}`). Qualquer tentativa de instanciar um transportador na quarentena é barrada com `ConfiguracaoInvalida`.
- O handoff entre a coleta e a entrega final ocorre via Observer: ao aprovar o lote (`lote_aprovado`), o observador `DespachanteTransporte` assume os itens aprovados, carrega o `RoboTransportador` e despacha a entrega até o ponto de retirada `(9, 9)`, emitindo `transporte_concluido`.

---

## Mapeamento para as aulas da disciplina

| Mecanismo / Conceito | Módulo / Arquivo | Classe / Símbolo | Descrição no Projeto |
|---|---|---|---|
| **Fundamentos de OO & Herança** | `src/celular_robo/robo.py` | `RoboColetor(Robo)`, `RoboTransportador(Robo)` | Herdam da base `Robo`, reutilizando sistema de movimentação, coordenadas e registro. |
| **Métodos Especiais (`__repr__`, `__len__`)** | `src/celular_robo/robo.py` | `RoboColetor`, `RoboTransportador`, `Bandeja` | `len()` conta o total de aparelhos ou carga; `__repr__` dá a representação textual para debug. |
| **Descriptors** | `src/celular_robo/robo.py` | `QuantidadeValida` | Descriptor que valida o dicionário de itens e impede valores negativos ou acima do limite. |
| **Metaprogramação (`__init_subclass__`)** | `src/celular_robo/robo_base.py`, `src/celular_robo/estrategias.py` | `Robo._registro`, `RotaColeta._registro` | Registro automático de robôs (`RoboColetor`, `RoboTransportador`) e rotas (`direta`, `dupla_conferencia`). |
| **Strategy Pattern** | `src/celular_robo/estrategias.py` | `RotaDireta`, `RotaComDuplaConferencia` | Algoritmos intercambiáveis de rota (coleta direta vs. com dupla conferência). |
| **Command Pattern** | `src/celular_robo/comandos.py` | `ComandoColeta` | Encapsula a ação de coleta com `executar()` para coletar e `desfazer()` para rollback. |
| **Factory Pattern** | `src/celular_robo/fabrica.py` | `criar_robo_configurado` | Centraliza a validação e montagem do robô a partir do modelo de features. |
| **Observer Pattern** | `src/celular_robo/observadores.py` | `EquipeDeTestes`, `RegistroAuditoria`, `MonitorBandeja`, `DespachanteTransporte` | Disparo e escuta de eventos (`bandeja_pronta`, `lote_aprovado`, `transporte_concluido`) e histórico. |
| **State Pattern** | `src/celular_robo/modos.py` | `ModoColetando`, `ModoAguardandoVerificacao` | Estados do robô: operando normalmente vs. bloqueado aguardando liberação da bancada. |
| **Linha de Produtos de Software (LPS)** | `src/celular_robo/modelo_features.py` | `validar_configuracao`, `REQUER`, `EXCLUI` | Matriz de compatibilidade entre robô, área e estratégia (ex.: quarentena exclui direta e transportador). |
| **Hierarquia de Exceções** | `src/celular_robo/excecoes.py` | `ErroColeta`, `ConfiguracaoInvalida`, `PedidoInvalido` | Exceções customizadas com herança para tratamento genérico ou granular. |
| **Persistência / Serialização** | `src/celular_robo/persistencia.py` | `montar_robo_de_config`, `montar_pedido_de_json` | Leitura de arquivos JSON para montagem do robô e dos lotes de pedidos. |
| **Testes Automatizados (`pytest`)** | `tests/` | 30 testes em `test_*.py` | Cobertura de contratos, regras da LPS, obstáculos, fluxo de estados e transportador. |
| **Interface CLI** | `src/celular_robo/cli.py` | `CLIApp`, `main` | Menu interativo no terminal para testar todo o fluxo do laboratório. |
