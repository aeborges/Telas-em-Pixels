# Research: Mapa de pixels

**Feature**: `001-mapa-de-pixels` | **Date**: 2026-08-19

## 1. Toolkit GUI: Tkinter vs Qt

- **Decision**: Tkinter.
- **Rationale**: Continuação do projeto irmão Paleta de Cores (mesmo
  usuário, mesmo tipo de utilitário desktop, mesmo lançador `.pyw`).
  Zero peso de Qt no ambiente do usuário. Overlay e dica são janelas
  `Toplevel` sem borda, sempre no topo.
- **Alternatives considered**: PySide6/PyQt — melhor RGBA e
  `WindowTransparentForInput` nativo, porém dependência pesada e
  ruptura com o padrão já adotado.

## 2. Click-through do overlay

- **Decision**: estilo estendido por plataforma, aplicado depois da
  janela mapear.
  - Windows: `WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW` via
    ctypes; chroma-key `-transparentcolor` para “buracos” de verdade.
  - Linux/X11: `XShapeCombineRectangles` em `ShapeInput` com zero
    retângulos (a janela desenha mas não recebe evento).
  - macOS: `ignoresMouseEvents` via PyObjC se existir; senão melhor
    esforço com estilo `noActivates`.
- **Rationale**: Tk não oferece API portátil. ctypes evita
  `python-xlib` / PyWin32.
- **Alternatives considered**: janela com alpha global (diming da tela
  inteira, ainda captura clique) — rejeitado no Windows porque quebra
  FR-004.

## 3. Enumeração de monitores

- **Decision**: `screeninfo` com fallback: Windows
  `EnumDisplayMonitors`; senão um único retângulo `winfo_screenwidth /
  height`.
- **Rationale**: `screeninfo` cobre Win/Linux/macOS com API estável.
  Fallback evita app inútil se a lib falhar.
- **Alternatives considered**: só Tk (`winfo_vrootwidth`) — não
  distingue monitores. Qt `QScreen` — depende de Qt.

## 4. PDF

- **Decision**: reportlab Canvas. Tamanhos nomeados (A5–A3, Letter,
  Legal, Tabloid). Retrato = (min, max) do par; paisagem = (max, min).
  Mapa escalado com `min(area/w, area/h)` para caber numa página.
- **Rationale**: controle total de régua, texto e imagem; MediaBox
  verificável em teste.
- **Alternatives considered**: fpdf2 (API mais pobre para ticks);
  matplotlib (pesado); SVG (não pedido).

## 5. Captura da tela

- **Decision**: `mss` recortando o retângulo em coords do desktop
  virtual. Overlay e dica são ocultados durante o grab. Pillow só para
  entregar a imagem ao reportlab.
- **Rationale**: `ImageGrab` é frágil no Linux e em multi-monitor.
  `mss` usa DXGI/X11/CGDisplay.
- **Alternatives considered**: Pillow ImageGrab; scrot via subprocess.

## 6. DPI

- **Decision**: no Windows, `SetProcessDpiAwareness(2)`
  (per-monitor) no boot, antes de criar janelas Tk.
- **Rationale**: sem isso o mapa mente em escalas 125%/150%.
- **Alternatives considered**: ignorar DPI — viola princípio VI.

## 7. Dois pontos → retângulo

- **Decision**: pixels inclusivos: `largura = abs(x2-x1)+1`. Qualquer
  ordem dos pontos. Interseção com o monitor ativo antes do PDF.
- **Rationale**: “ponto A até ponto B” inclui os dois pixels clicados.
  Região cross-monitor ficaria ambígua no mapa local.

## 8. Dica do cursor

- **Decision**: `Toplevel` click-through, posição `(cursor + 12, +24)`
  com flip perto das bordas; polling `winfo_pointerxy` a 16–33 ms no
  painel (funciona mesmo com overlay atravessável).
- **Rationale**: não depende de hook global (`pynput`), que exigiria
  permissão de acessibilidade no macOS.
- **Alternatives considered**: pynput; tooltip do próprio overlay
  (some quando click-through come os motion events — no Windows
  `WS_EX_TRANSPARENT` não entrega motion à janela, por isso o polling
  tem de ser no painel).
