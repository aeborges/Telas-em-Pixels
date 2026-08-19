# Feature Specification: Mapa de pixels do(s) monitor(es)

**Feature Branch**: `001-mapa-de-pixels`

**Created**: 2026-08-19

**Status**: Draft

**Input**: Aplicativo GUI Python que apresenta um mapa de pixels (régua
10/100 px) em transparência sobre o monitor escolhido, sem bloquear a
interação com a tela; dica de coordenadas no cursor; geração de PDF do
monitor inteiro ou de um retângulo definido por dois pontos, com tamanho
de página e orientação escolhidos pelo usuário.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver o mapa de pixels no monitor escolhido (Priority: P1)

Quem precisa medir a tela abre o aplicativo, escolhe o monitor (quando
há mais de um) e vê sobre aquele monitor um mapa transparente no estilo
régua: marcas inteiras a cada 100 px e frações a cada 10 px. Pode
continuar clicando e digitando nas janelas de baixo.

**Why this priority**: Sem o overlay medidor o restante do produto não
existe. É o MVP.

**Independent Test**: Abrir o app com um ou mais monitores simulados;
confirmar que o overlay cobre só o monitor selecionado, desenha marcas
10/100 e, no modo normal, não consome cliques.

**Acceptance Scenarios**:

1. **Given** um computador com um único monitor, **When** o app inicia
   com “mostrar mapa” ligado, **Then** o overlay cobre esse monitor e
   exibe régua/grade 10 px e 100 px com origem (0,0) no canto superior
   esquerdo daquele monitor.
2. **Given** dois ou mais monitores, **When** o usuário escolhe o
   monitor N no painel, **Then** o overlay sai do monitor anterior e
   passa a cobrir apenas o N, com coordenadas locais daquele monitor.
3. **Given** o mapa visível em modo normal, **When** o usuário clica
   numa janela que está “abaixo” do overlay, **Then** o clique chega a
   essa janela (o overlay é atravessável).

---

### User Story 2 - Coordenada do cursor em tempo real (Priority: P1)

Enquanto o mapa está ativo, uma dica pequena abaixo do cursor mostra a
coordenada em pixels do ponto apontado, atualizada continuamente.

**Why this priority**: Medir sem saber o (x, y) atual obriga a contar
marcas à mão. Complementa o MVP.

**Independent Test**: Mover o ponteiro sobre o monitor mapeado e
observar a dica acompanhar, abaixo do cursor, com x/y locais; fora do
monitor mapeado a dica indica que está fora.

**Acceptance Scenarios**:

1. **Given** mapa ativo no monitor M, **When** o cursor está sobre M,
   **Then** a dica abaixo do cursor mostra `x` e `y` inteiros relativos
   a M, atualizados em tempo real.
2. **Given** a dica visível, **When** o cursor chega perto da borda
   inferior/direita, **Then** a dica desloca-se para permanecer
   visível (não some cortada).
3. **Given** a dica visível, **When** o usuário clica através dela,
   **Then** o clique não é engolido pela dica.

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
   **Then** a imagem da tela (sem o overlay) aparece sob a grade.

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
3. **Given** o primeiro ponto já clicado, **When** o usuário pressiona
   Esc, **Then** a seleção é abortada, o overlay volta a ser
   atravessável e nenhum PDF é gerado.
4. **Given** modo de seleção, **When** o usuário move o mouse após o
   primeiro clique, **Then** um retângulo elástico mostra a área que
   será mapeada.

---

### Edge Cases

- Dois pontos iguais: retângulo de 1×1 px; PDF ainda é gerado com aviso
  no cabeçalho.
- Região que atravessa dois monitores: recortada ao monitor ativo (só
  o trecho sobre o monitor escolhido entra no mapa).
- Cursor fora de qualquer monitor conhecido: dica “fora”.
- Falha ao gravar PDF (disco, permissão): mensagem no painel, overlay
  restaurado.
- Um único monitor: o seletor existe, mas já vem preenchido; não exige
  escolha extra.
- Desligar “mostrar mapa”: overlay e dica somem; o painel permanece.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST enumerar os monitores conectados e permitir
  escolher qual recebe o mapa quando houver mais de um.
- **FR-002**: O sistema MUST desenhar sobre o monitor escolhido um mapa
  no estilo régua, com marcas a cada 100 px (inteiro) e a cada 10 px
  (fração), origem no canto superior esquerdo daquele monitor.
- **FR-003**: O mapa MUST ser visualmente transparente o bastante para
  ver o conteúdo da tela.
- **FR-004**: Em modo normal o overlay e a dica MUST deixar passar
  cliques e interação com as janelas abaixo.
- **FR-005**: O sistema MUST exibir abaixo do cursor, em tempo real, a
  coordenada em pixels do ponto apontado (referente ao monitor
  mapeado).
- **FR-006**: O usuário MUST poder gerar PDF do monitor inteiro.
- **FR-007**: O usuário MUST poder definir um retângulo por dois pontos
  na tela e gerar o PDF só desse trecho.
- **FR-008**: O usuário MUST escolher tamanho de página (no mínimo A4,
  A3, A5, Letter, Legal, Tabloid) e orientação Retrato ou Paisagem
  antes de gerar o PDF; o PDF MUST indicar essas escolhas.
- **FR-009**: Durante a seleção por dois pontos o overlay MAY capturar
  cliques; ao terminar ou cancelar MUST voltar ao modo atravessável.
- **FR-010**: O PDF MUST trazer a grade/régua na escala da região, com
  as coordenadas reais da seleção.
- **FR-011**: O usuário MUST poder incluir ou não a captura da tela
  (sem overlay) como fundo do mapa no PDF.
- **FR-012**: A interface MUST estar em português do Brasil.

### Key Entities

- **Monitor**: retângulo no desktop virtual (origem, largura, altura,
  nome, se é primário).
- **Ponto**: par inteiro (x, y) em pixels.
- **Retângulo de seleção**: eixo-alinhado definido por dois pontos
  inclusivos.
- **Especificação da régua**: passo menor (10) e maior (100).
- **Opções de PDF**: tamanho de página, orientação, incluir captura.
- **Mapa**: combinação de régua + região + (opcional) imagem.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Com o mapa ligado, um clique numa janela coberta pelo
  overlay é recebido por essa janela (não pelo app), verificável no
  Windows e, no melhor esforço, em Linux/macOS.
- **SC-002**: A dica de coordenadas atualiza com latência percebida
  abaixo de ~50 ms (polling ≤ 33 ms).
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
  macOS suportados no melhor esforço para overlay atravessável.
- Tkinter é o toolkit GUI, em continuidade com o projeto irmão.
- Não há backend, conta de usuário nem rede.
- “Pixels” são os pixels lógicos do espaço do monitor após DPI-aware
  no Windows.
- Impressão física do PDF usa a escala declarada no cabeçalho; não se
  garante 1 px = 1 mm no papel.
