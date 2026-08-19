# Mapa de pixels dos monitores

Aplicativo para Windows 10/11 que mostra uma grade transparente sobre o monitor escolhido, sem bloquear cliques durante o uso normal, informa coordenadas do cursor, permite selecionar um retangulo por dois pontos e exporta o mapa vetorial da area para PDF A4.

## Instalacao

```powershell
py -m pip install -r requirements_mapa_pixels.txt
```

## Execucao

```powershell
py mapa_pixels_monitores.py
```

## Uso

1. Escolha o monitor.
2. Ajuste a opacidade da grade.
3. Use `Selecionar por 2 pontos` e clique nos dois cantos opostos. Durante essa operacao, o overlay captura os dois cliques; depois volta automaticamente ao modo permeavel a cliques. `Esc` cancela.
4. Como alternativa, use `Usar tela inteira`.
5. Escolha `Automatica`, `Portrait` ou `Landscape` e gere o PDF.

## Gerar executavel Windows

```powershell
py -m pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name MapaPixelsMonitores mapa_pixels_monitores.py
```

O executavel sera criado em `dist`.

## Observacoes tecnicas

- A aplicacao ativa DPI awareness por monitor antes de iniciar o Qt, para trabalhar com coordenadas fisicas em configuracoes de escala do Windows.
- A grade usa divisao menor de 10 px e marcacao principal de 100 px.
- O PDF contem um mapa vetorial da regiao, com coordenadas locais do monitor e origem global do desktop virtual. Ele nao captura nem incorpora o conteudo visual da tela.
- Se monitores estiverem posicionados a esquerda ou acima do principal, coordenadas globais negativas sao normais.
