# Quickstart — validação da feature

## Ambiente

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
# Linux: sudo apt-get install -y python3-tk
```

## Testes (sem GUI)

```bash
python -m pytest tests/ -q
```

Esperado: todos os unitários de geometria, régua, página e PDF verdes.
O teste de PDF grava em diretório temporário e checa cabeçalho +
MediaBox retrato/paisagem.

## Demo de PDF sem overlay

```bash
python -m telas_em_pixels --demo-pdf /tmp/mapa-demo.pdf
```

Esperado: arquivo PDF de uma página A4 paisagem com régua de uma região
sintética 800×500.

## GUI (máquina com display)

```bash
python main.py
# ou, no Windows, duplo clique em Mapa_de_Pixels.pyw
```

Passos manuais (SC-005):

1. Escolher o monitor se houver mais de um.
2. Confirmar mapa 10/100 px sobre esse monitor.
3. Clicar numa janela abaixo — o clique deve passar.
4. Mover o cursor — dica com x/y abaixo do ponteiro.
5. Gerar PDF do monitor (A4 paisagem).
6. Selecionar região com dois cliques e gerar outro PDF (A4 retrato).
7. Esc no meio da seleção cancela.

## Critério de pronto

`pytest` verde + demo-pdf gera arquivo válido + checklist de
`checklists/requirements.md` marcada.
