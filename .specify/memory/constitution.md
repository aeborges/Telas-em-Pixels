# Constituição — Telas em Pixels

Princípios obrigatórios deste repositório. Qualquer plano, tarefa ou
implementação deve passar pelo Constitution Check antes de avançar.

## Princípios centrais

### I. Especificação antes do código (SDD)

Nenhuma funcionalidade entra no código sem artefatos SDD da feature:
`spec.md` (o quê e por quê), `plan.md` (como), `tasks.md` (passos
executáveis). O código implementa a spec; a spec não é reescrita para
caber no código. Mudança de requisito → atualizar spec → então o código.

### II. Interface em português do Brasil

Textos visíveis ao usuário, nomes de domínio e comentários que explicam
*por quê* ficam em pt-BR. Identificadores técnicos de bibliotecas
externas (Tk, PDF, pytest) permanecem no idioma da API.

### III. Domínio puro, GUI na borda

Regras de geometria, régua, página PDF e modelo de monitor vivem em
módulos sem Tkinter. Testes unitários não exigem display. A GUI só
orquestra: detecta monitores, desenha, captura clique, chama o domínio.

### IV. Overlay não-intrusivo

O mapa sobre a tela **não pode** impedir cliques nem teclado nas
aplicações de baixo, salvo no modo explícito de seleção de região. A
dica de coordenadas segue o cursor sem roubar foco. O painel de controle
é a única janela que captura interação continuamente.

### V. Poucas dependências, lançamento simples

Preferir biblioteca padrão. Dependências externas só quando o stdlib
não cobre (PDF, captura multi-monitor). No Windows o usuário abre o
`.pyw` com duplo clique, sem console — o mesmo padrão do utilitário
Paleta de Cores (projeto irmão). `python main.py` permanece para
depuração.

### VI. Medida em pixels reais do monitor

Coordenadas, marcas de 10 px / 100 px e o PDF descrevem o espaço em
pixels do monitor escolhido (origem no canto superior esquerdo daquele
monitor). Escala de DPI do sistema deve ser respeitada para o mapa não
mentir.

## Regras de engenharia

- Testes do domínio acompanham cada história de usuário; pytest é a
  suíte. GUI pode ter fumaça opcional, nunca bloqueia o domínio.
- Falhas de I/O (salvar PDF, captura) viram mensagem clara na interface,
  nunca traceback cru para o usuário final.
- Código morto, nomes em inglês misturados no domínio e atalhos que
  quebram o click-through são violações desta constituição.

## Governança

Esta constituição prevalece sobre hábitos do implementador e sobre
conveniências de biblioteca. Emenda exige atualizar `spec`/`plan` da
feature afetada e o campo Version abaixo.

**Version**: 1.0.0 | **Ratified**: 2026-08-19 | **Last Amended**: 2026-08-19
