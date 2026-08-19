# Telas em Pixels

Aplicativo desktop em Python que desenha um **mapa de pixels** (régua
de 10 px / 100 px) em transparência sobre o monitor escolhido, mostra a
coordenada do cursor em tempo real e exporta o mapa — da tela inteira ou
de um retângulo definido por dois pontos — para **PDF** no tamanho e na
orientação que você escolher.

Especificação, plano e tarefas seguem SDD (Spec-Driven Development):
veja [`specs/001-mapa-de-pixels/`](specs/001-mapa-de-pixels/).

## Funcionalidades

- Escolha do monitor quando há mais de um.
- Overlay no estilo régua: marcas inteiras a cada **100 px**, frações a
  cada **10 px**, origem `(0, 0)` no canto superior esquerdo daquele
  monitor.
- Transparência sobre a tela; no modo normal os cliques **passam** para
  as janelas de baixo (Windows com chroma-key + `WS_EX_TRANSPARENT`;
  Linux/X11 via shape de input; macOS no melhor esforço).
- Dica abaixo do cursor com `x` e `y` locais, atualizada em tempo real.
- PDF do monitor inteiro ou de uma região (dois cliques, qualquer
  ordem; Esc cancela).
- Tamanhos A5, A4, A3, Letter, Legal, Tabloid · Retrato ou Paisagem —
  declarados no cabeçalho do PDF.
- Opção de incluir a captura da tela (sem o overlay) como fundo do mapa.

## Rodar

```bash
python -m pip install -r requirements.txt
python main.py
```

No Windows, para abrir sem a janela preta do terminal, dê duplo clique
em `Mapa_de_Pixels.pyw` (ou `pythonw Mapa_de_Pixels.pyw`).

Linux: além do pip, instale o Tk:

```bash
sudo apt-get install python3-tk
```

PDF de demonstração sem GUI:

```bash
python -m telas_em_pixels --demo-pdf mapa-demo.pdf
```

## Testes

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

## Estrutura

```
telas_em_pixels/dominio/     geometria, régua, página, PDF (sem Tk)
telas_em_pixels/plataforma/  monitores, captura, click-through, DPI
telas_em_pixels/ui/          painel, overlay, dica
specs/001-mapa-de-pixels/    SDD (spec, plan, tasks)
```

## Limitações conhecidas

- O click-through é nativo e confiável no **Windows**. No Linux depende
  do compositor/X11; no macOS, de PyObjC (`ignoresMouseEvents`).
- A escala do PDF cabe o mapa numa página: 1 px da tela **não** vira
  1 mm no papel — o fator real vai no rodapé do PDF.
- Coordenadas são pixels lógicos do monitor (DPI-aware no Windows).

## Licença

MIT — veja [LICENSE](LICENSE).
