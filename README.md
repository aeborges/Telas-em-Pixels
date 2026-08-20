# Telas em Pixels

Aplicativo desktop em Python que mostra a **coordenada do ponteiro em
tempo real**, gera um **mapa de pixels** da região que você definir
(digitando dois pontos ou clicando na tela) e exporta esse mapa para
**PDF** no tamanho e na orientação escolhidos.

Especificação, plano e tarefas seguem SDD (Spec-Driven Development):
veja [`specs/001-mapa-de-pixels/`](specs/001-mapa-de-pixels/).

## Funcionalidades

- Coordenadas `x` / `y` do ponteiro ao abrir o app, atualizadas ao vivo
  (posição global e posição no monitor escolhido).
- Escolha do monitor quando há mais de um.
- Região do mapa por **dois pontos**: digitados no painel, capturados
  com **F8** (posição atual do ponteiro) ou por clique fora da janela;
  atalho “Usar o monitor inteiro”.
- Grade configurável: distância das **linhas principais** (mais escuras
  e um pouco mais grossas) e das **secundárias** (mais finas e claras).
  Cores à escolha, com tons padrão **#BDBDBD** (cinza 74) e **#D6D6D6**
  (cinza 84).
- PDF do monitor inteiro ou da região definida.
- Tamanhos A5, A4, A3, Letter, Legal, Tabloid · Retrato ou Paisagem —
  declarados no cabeçalho do PDF.
- Opção de incluir a captura da tela como fundo do mapa (na janela e no
  PDF).

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
telas_em_pixels/dominio/     geometria, régua/grade, página, PDF (sem Tk)
telas_em_pixels/plataforma/  monitores, captura, ponteiro, DPI
telas_em_pixels/ui/          painel e canvas do mapa
specs/001-mapa-de-pixels/    SDD (spec, plan, tasks)
```

## Limitações conhecidas

- A escala do PDF cabe o mapa numa página: 1 px da tela **não** vira
  1 mm no papel — o fator real vai no rodapé do PDF.
- Coordenadas são pixels lógicos do monitor (DPI-aware no Windows).
- F8 registra o pixel sob o ponteiro sem clicar no aplicativo de baixo.
  Um clique fora da janela também registra o ponto, mas o clique chega
  ao programa que está atrás.

## Licença

MIT — veja [LICENSE](LICENSE).
