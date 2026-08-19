# Feature Specification: Mapa de pixels do(s) monitor(es)

**Feature Branch**: `001-mapa-de-pixels`

**Created**: 2026-08-19

**Status**: Draft

**Input**: Aplicativo GUI Python que mostra a coordenada do ponteiro em
tempo real, gera um mapa de pixels (grade configurável) da região
definida por dois pontos — digitados ou clicados na tela — e exporta
PDF do monitor inteiro ou dessa região, com tamanho de página e
orientação escolhidos pelo usuário. Sem overlay cobrindo o monitor.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver o mapa de pixels da região definida (Priority: P1)

Quem precisa medir a tela abre o aplicativo, escolhe o monitor (quando
há mais de um) e define uma região — digitando dois pontos ou
clicando/capturando na tela. O app desenha o mapa de pixels **na própria
janela**: linhas principais (mais escuras) e secundárias (mais finas e
claras), com distâncias e cores escolhidas pelo usuário (padrão 100 px
em #BDBDBD e 10 px em #D6D6D6). Origem (0, 0) no canto superior
esquerdo daquele monitor.

**Why this priority**: Sem o mapa da região o restante do produto não
existe. É o MVP.

**Independent Test**: Abrir o app, informar dois pontos (ou o monitor
inteiro) e confirmar que o canvas mostra a grade com os passos e cores
configurados.

**Acceptance Scenarios**:

1. **Given** um computador com um único monitor, **When** o usuário
   define a região do monitor inteiro, **Then** o mapa na janela cobre
   essa resolução e exibe grade com origem (0,0) no canto superior
   esquerdo daquele monitor.
2. **Given** dois ou mais monitores, **When** o usuário escolhe o
   monitor N no painel, **Then** as coordenadas e o recorte da região
   passam a ser locais daquele monitor.
3. **Given** o app aberto, **When** o usuário trabalha em outras
   janelas, **Then** não há overlay cobrindo a tela — só o painel do
   app.

---

### User Story 2 - Coordenada do ponteiro em tempo real (Priority: P1)

Ao abrir o app, o painel mostra a coordenada em pixels do ponteiro,
atualizada continuamente (posição global e posição no monitor
escolhido). Fora desse monitor, indica que está fora.

**Why this priority**: Medir sem saber o (x, y) atual obriga a contar
marcas à mão. Complementa o MVP.

**Independent Test**: Mover o ponteiro e observar x/y no painel; fora
do monitor escolhido o texto indica “fora”.

**Acceptance Scenarios**:

1. **Given** o app aberto com o monitor M selecionado, **When** o
   cursor está sobre M, **Then** o painel mostra `x` e `y` inteiros
   globais e locais a M, atualizados em tempo real.
2. **Given** o ponteiro visível no painel, **When** o cursor sai de M,
   **Then** o painel indica que está fora do monitor selecionado.
3. **Given** o ponteiro sobre a região mapeada, **When** o mapa já foi
   gerado, **Then** um marcador no canvas acompanha a posição local.

---

### User Story 3 - PDF do monitor inteiro (Priority: P2)

O usuário escolhe tamanho de página (A4, A3, Letter, etc.) e orientação
(retrato ou paisagem) e gera um PDF com o mapa de pixels do monitor
selecionado por inteiro.

**Why this priority**: Entrega o artefato imprimível da tela completa,
pedido explícito.

**Independent Test**: Gerar PDF em retrato e paisagem, tamanhos
diferentes, a partir de um retângulo do tamanho do monitor; o arquivo
abre, declara orientação/tamanho e contém a grade com coordenadas.

**Acceptance Scenarios**:

1. **Given** monitor 1920×1080 selecionado, página A4 paisagem,
   **When** o usuário pede “PDF do monitor inteiro”, **Then** um PDF é
   gravado com página paisagem A4, mapa 1920×1080 px escalado para
   caber, régua 10/100 e metadados (tamanho real, escala, orientação).
2. **Given** as mesmas dimensões, **When** o usuário escolhe retrato,
   **Then** a página do PDF é retrato e o mapa reescala para caber
   nessa folha.
3. **Given** opção de incluir captura ligada, **When** o PDF é gerado,
   **Then** a imagem da tela aparece sob a grade.

---

### User Story 4 - PDF de uma região por dois pontos (Priority: P2)

O usuário indica dois pontos na tela; esses pontos definem um retângulo.
O app gera o mapa de pixels só daquele trecho, no tamanho/orientação já
escolhidos.

**Why this priority**: É o fluxo pedido para “partes da tela”, distinto
do monitor inteiro.

**Independent Test**: Dois pontos em qualquer ordem (inclusive
invertidos) produzem o retângulo canônico; PDF cobre exatamente essa
região; Esc cancela a seleção.

**Acceptance Scenarios**:

1. **Given** modo “selecionar região”, **When** o usuário clica o ponto
   A e depois o ponto B, **Then** o retângulo é o menor eixo-alinhado
   que inclui ambos os pixels (ordem dos cliques irrelevante).
2. **Given** seleção concluída, **When** o PDF é gerado, **Then** as
   marcas da régua usam coordenadas de tela/monitor da região (não
   recomeçam em 0,0 a menos que a região comece na origem).
3. **Given** o primeiro ponto já capturado, **When** o usuário pressiona
   Esc, **Then** a seleção é abortada e nenhum PDF é gerado.
4. **Given** os dois pontos informados (digitados ou capturados),
   **When** ambos são válidos, **Then** o mapa da região aparece no
   canvas da janela.

---

### Edge Cases

- Dois pontos iguais: retângulo de 1×1 px; PDF ainda é gerado com aviso
  no cabeçalho.
- Região que atravessa dois monitores: recortada ao monitor ativo (só
  o trecho sobre o monitor escolhido entra no mapa).
- Cursor fora do monitor escolhido: painel indica “fora”.
- Falha ao gravar PDF (disco, permissão): mensagem no painel.
- Um único monitor: o seletor existe, mas já vem preenchido; não exige
  escolha extra.
- Região ainda não definida: o canvas mostra um convite a informar os
  dois pontos; o ponteiro já aparece ao vivo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST enumerar os monitores conectados e permitir
  escolher qual recebe o mapa quando houver mais de um.
- **FR-002**: O sistema MUST desenhar na janela do app um mapa da
  região definida, com linhas principais e secundárias, origem no canto
  superior esquerdo daquele monitor.
- **FR-003**: O usuário MUST poder alterar a distância das linhas
  principais e das secundárias.
- **FR-004**: O usuário MUST poder escolher as cores da grade; os tons
  padrão são #BDBDBD (principais) e #D6D6D6 (secundárias). Linhas
  principais são mais escuras; secundárias, mais finas e mais claras.
- **FR-005**: O sistema MUST exibir no painel, ao abrir o app e em
  tempo real, a coordenada em pixels do ponteiro (global e local ao
  monitor escolhido).
- **FR-006**: O usuário MUST poder gerar PDF do monitor inteiro.
- **FR-007**: O usuário MUST poder definir um retângulo por dois pontos
  (digitando ou clicando/capturando na tela) e gerar o mapa e o PDF só
  desse trecho.
- **FR-008**: O usuário MUST escolher tamanho de página (no mínimo A4,
  A3, A5, Letter, Legal, Tabloid) e orientação Retrato ou Paisagem
  antes de gerar o PDF; o PDF MUST indicar essas escolhas.
- **FR-009**: Durante a captura por dois pontos o sistema MUST aceitar
  F8 (posição atual do ponteiro) e clique fora da janela; Esc cancela.
- **FR-010**: O PDF MUST trazer a grade/régua na escala da região, com
  as coordenadas reais da seleção.
- **FR-011**: O usuário MUST poder incluir ou não a captura da tela
  como fundo do mapa na janela e no PDF.
- **FR-012**: A interface MUST estar em português do Brasil.

### Key Entities

- **Monitor**: retângulo no desktop virtual (origem, largura, altura,
  nome, se é primário).
- **Ponto**: par inteiro (x, y) em pixels.
- **Retângulo de seleção**: eixo-alinhado definido por dois pontos
  inclusivos.
- **Especificação da régua / estilo da grade**: passo menor e maior
  (padrão 10 e 100) e cores (padrão #BDBDBD e #D6D6D6).
- **Opções de PDF**: tamanho de página, orientação, incluir captura.
- **Mapa**: combinação de régua + região + (opcional) imagem.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Não há janela cobrindo o monitor; cliques nas outras
  aplicações não são interceptados pelo app, salvo no instante em que
  o usuário pede para capturar um ponto.
- **SC-002**: As coordenadas do ponteiro no painel atualizam com
  latência percebida abaixo de ~50 ms (polling ≤ 33 ms).
- **SC-003**: PDF gerado abre em leitor comum, página no tamanho e
  orientação pedidos, com régua 10/100 e dimensões da região no
  cabeçalho.
- **SC-004**: Dois pontos em qualquer octante produzem o mesmo
  retângulo canônico (propriedade coberta por teste unitário).
- **SC-005**: Usuário consegue completar “escolher monitor → ver mapa →
  exportar PDF” sem documentação externa, só com rótulos do painel.

## Assumptions

- Público: quem desenha/interfaceia e precisa medir pixels na tela
  (mesmo perfil da Paleta de Cores Tkinter).
- Plataforma alvo: Windows em primeiro plano (lançador `.pyw`); Linux e
  macOS suportados no melhor esforço (F8 para capturar o ponto).
- Tkinter é o toolkit GUI, em continuidade com o projeto irmão.
- Não há backend, conta de usuário nem rede.
- “Pixels” são os pixels lógicos do espaço do monitor após DPI-aware
  no Windows.
- Impressão física do PDF usa a escala declarada no cabeçalho; não se
  garante 1 px = 1 mm no papel.
