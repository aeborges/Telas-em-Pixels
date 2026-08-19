# Implementation Plan: Mapa de pixels do(s) monitor(es)

**Branch**: `001-mapa-de-pixels` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-mapa-de-pixels/spec.md`

## Summary

Aplicativo desktop Tkinter que (1) lista monitores, (2) desenha um
overlay de régua 10/100 px no monitor escolhido sem roubar cliques,
(3) mostra (x, y) numa dica abaixo do cursor e (4) exporta o mapa da
região — monitor inteiro ou retângulo de dois pontos — para PDF com
tamanho e orientação escolhidos. O domínio (geometria, régua, página,
desenho PDF) é puro e testável; a GUI e os ganchos de SO ficam na borda.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: Tkinter (stdlib / python3-tk); reportlab
(PDF); Pillow (imagem no PDF); screeninfo (enumeração de monitores);
mss (captura multi-monitor). ctypes para click-through e DPI no
Windows/X11.

**Storage**: N/A (arquivo PDF escolhido pelo usuário a cada exportação)

**Testing**: pytest; testes unitários sem display; PDF inspecionado
como bytes (`%PDF`, MediaBox)

**Target Platform**: Windows (primário), Linux X11 e macOS (melhor
esforço no click-through)

**Project Type**: desktop-app

**Performance Goals**: overlay estático (redesenho ao trocar monitor);
dica ≤ 33 ms; PDF de um Full HD em poucos segundos

**Constraints**: overlay atravessável; app DPI-aware no Windows;
dependências mínimas; UI pt-BR; lançador `.pyw`

**Scale/Scope**: 1–N monitores de uma estação; uma região por PDF;
sem serviço de rede

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Como |
|-----------|--------|------|
| I. SDD | PASS | spec, plan, research, data-model, contracts, tasks, checklist |
| II. pt-BR | PASS | painel, dica, PDF e nomes de domínio em português |
| III. Domínio puro | PASS | `telas_em_pixels/dominio/` sem Tk; testes em `tests/unit/` |
| IV. Overlay não-intrusivo | PASS | click-through por plataforma; seleção é modo explícito |
| V. Poucas deps + `.pyw` | PASS | 4 libs + stdlib; `Mapa_de_Pixels.pyw` |
| VI. Pixels reais | PASS | DPI-aware Windows; coords locais do monitor |

Re-check pós-design: sem violação a registrar em Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-mapa-de-pixels/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dominio.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
telas_em_pixels/
├── __init__.py
├── __main__.py
├── app.py                 # orquestra painel + overlay + dica
├── dominio/
│   ├── geometria.py       # Ponto, Retangulo
│   ├── regua.py           # marcas 10 / 100
│   ├── pagina.py          # tamanhos, orientação, escala
│   └── pdf.py             # gera o arquivo PDF
├── plataforma/
│   ├── monitores.py       # enumeração (screeninfo + fallback)
│   ├── captura.py         # screenshot da região
│   ├── click_through.py   # Win/X11/macOS
│   └── dpi.py             # SetProcessDpiAwareness
└── ui/
    ├── tema.py
    ├── painel.py
    ├── overlay.py
    └── dica.py
main.py
Mapa_de_Pixels.pyw
tests/unit/
tests/integration/
```

**Structure Decision**: pacote único na raiz (`telas_em_pixels/`), no
mesmo espírito do utilitário Paleta (entrada `main.py` + lançador
`.pyw`), com domínio separado para cumprir o princípio III.

## Complexity Tracking

> Nenhuma violação da constituição.
