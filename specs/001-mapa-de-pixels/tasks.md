# Tasks: Mapa de pixels do(s) monitor(es)

**Input**: Design documents from `/specs/001-mapa-de-pixels/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Sim — domínio puro e PDF, conforme constituição III.

**Organization**: Por história de usuário.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Criar estrutura de pacotes `telas_em_pixels/{dominio,plataforma,ui}` e `tests/{unit,integration}`
- [x] T002 [P] Adicionar `requirements.txt`, `requirements-dev.txt`, `.gitignore`
- [x] T003 [P] Adicionar `main.py`, `Mapa_de_Pixels.pyw`, `telas_em_pixels/__main__.py`

---

## Phase 2: Foundational

- [x] T004 [P] Implementar `Ponto` e `Retangulo` em `telas_em_pixels/dominio/geometria.py`
- [x] T005 [P] Testes de geometria em `tests/unit/test_geometria.py` (ordem dos pontos, 1×1, interseção)
- [x] T006 [P] Implementar marcas de régua em `telas_em_pixels/dominio/regua.py`
- [x] T007 [P] Testes de régua em `tests/unit/test_regua.py`
- [x] T008 [P] Tamanhos/orientação/escala em `telas_em_pixels/dominio/pagina.py`
- [x] T009 [P] Testes de página em `tests/unit/test_pagina.py`
- [x] T010 Enumeração de monitores + fallback em `telas_em_pixels/plataforma/monitores.py`
- [x] T011 DPI Windows em `telas_em_pixels/plataforma/dpi.py`

**Checkpoint**: domínio geométrico e de página testável sem GUI

---

## Phase 3: User Story 1 — Overlay no monitor (P1) 🎯 MVP

- [x] T012 [P] [US1] Tema visual em `telas_em_pixels/ui/tema.py`
- [x] T013 [US1] Click-through Win/X11/macOS em `telas_em_pixels/plataforma/click_through.py`
- [x] T014 [US1] Overlay régua 10/100 em `telas_em_pixels/ui/overlay.py`
- [x] T015 [US1] Painel: lista de monitores + toggle do mapa em `telas_em_pixels/ui/painel.py`
- [x] T016 [US1] Orquestração inicial em `telas_em_pixels/app.py` (troca de monitor reposiciona overlay)

**Checkpoint**: mapa visível no monitor escolhido; modo normal atravessável

---

## Phase 4: User Story 2 — Dica de coordenadas (P1)

- [x] T017 [US2] Dica abaixo do cursor em `telas_em_pixels/ui/dica.py` (flip nas bordas, click-through)
- [x] T018 [US2] Polling `winfo_pointerxy` no app e atualização da dica (coords locais / “fora”)

**Checkpoint**: dica em tempo real sem roubar cliques

---

## Phase 5: User Story 3 — PDF do monitor inteiro (P2)

- [x] T019 [P] [US3] `gerar_mapa_pdf` em `telas_em_pixels/dominio/pdf.py`
- [x] T020 [P] [US3] Testes PDF (bytes %PDF, MediaBox retrato/paisagem) em `tests/unit/test_pdf.py`
- [x] T021 [P] [US3] Captura mss em `telas_em_pixels/plataforma/captura.py` (esconde overlay)
- [x] T022 [US3] Controles de tamanho/orientação/captura + botão “PDF do monitor” no painel
- [x] T023 [US3] `--demo-pdf` em `__main__.py` / `app.py`

**Checkpoint**: PDF do monitor com indicação de página e orientação

---

## Phase 6: User Story 4 — Região por dois pontos (P2)

- [x] T024 [US4] Teste do retângulo canônico já coberto em T005; teste de recorte ao monitor em `tests/unit/test_geometria.py`
- [x] T025 [US4] Modo seleção no overlay: dois cliques, elástico, Esc cancela, depois restaura click-through
- [x] T026 [US4] Botão “Selecionar região” no painel → PDF da interseção com o monitor

**Checkpoint**: US1–US4 independentes e integradas no painel

---

## Phase 7: Polish

- [x] T027 [P] README.md (uso, `.pyw`, limitações por SO)
- [x] T028 Teste de integração demo-pdf em `tests/integration/test_demo_pdf.py`
- [x] T029 Rodar `pytest` e validar `quickstart.md`

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 (bloqueia histórias)
- US1 (Phase 3) após Phase 2
- US2 usa overlay/painel da US1
- US3 domínio PDF pode paralelizar com US1 após T008; UI PDF após US1
- US4 após US1 (precisa do overlay) e US3 (geração PDF)
- Polish ao final

## Implementation Strategy

MVP = Phase 1–4 (mapa + dica). Depois PDFs (Phase 5–6).
