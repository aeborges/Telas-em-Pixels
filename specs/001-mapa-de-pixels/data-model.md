# Data Model: Mapa de pixels

## Ponto

| Campo | Tipo | Regras |
|-------|------|--------|
| x | int | pixel, pode ser negativo no desktop virtual |
| y | int | pixel, eixo Y cresce para baixo |

## Retangulo

Eixo-alinhado, **inclusivo** nos dois cantos.

| Campo | Tipo | Regras |
|-------|------|--------|
| x, y | int | canto superior esquerdo (menor x, menor y) |
| largura, altura | int | ≥ 1 |

**Factory**: `de_dois_pontos(a, b)` → `x=min`, `y=min`,
`largura=abs(dx)+1`, `altura=abs(dy)+1`.

**Operações**: `x2`/`y2` (exclusivos à direita/baixo, iguais a
x+largura); `contem_ponto`; `intersecao` (None se vazio).

## Monitor

| Campo | Tipo | Regras |
|-------|------|--------|
| indice | int | 0-based, estável na sessão |
| nome | str | ex. “Monitor 1 (primário)” |
| x, y, largura, altura | int | posição no desktop virtual |
| primario | bool | |

`retangulo` global. `para_local(x, y)` → Ponto local ou None se fora.

## EspecificacaoRegua

| Campo | Padrão | Significado |
|-------|--------|-------------|
| passo_menor | 10 | frações da régua |
| passo_maior | 100 | marcas inteiras numeradas |

`marcas(inicio, tamanho, passo)` → múltiplos de `passo` em
`[inicio, inicio+tamanho)`.

## OpcoesPDF

| Campo | Valores |
|-------|---------|
| tamanho | A5, A4, A3, Letter, Legal, Tabloid |
| orientacao | retrato \| paisagem |
| incluir_captura | bool |

`pagina_em_pontos(tamanho, orientacao) → (w, h)` em pontos PostScript.
`escala_para_caber(src_w, src_h, dst_w, dst_h) → float`.

## Estado da seleção (UI, não persistido)

```
inativa → aguardando_primeiro → aguardando_segundo → (retângulo) → inativa
                ↑ Esc / cancelar ↙
```

Dois pontos são globais; o retângulo é intersectado com o monitor ativo
antes de gerar o PDF.

## MapaPDF (artefato)

Entrada: Retangulo (já local ou global consistente), OpcoesPDF, imagem
opcional, metadados de texto (nome do monitor, coords).

Saída: arquivo PDF de **uma** página. Cabeçalho declara região, escala
(px → pt), tamanho e orientação. Corpo: régua superior/esquerda, grade
100 px, ticks 10 px nas réguas, captura opcional sob a grade.
