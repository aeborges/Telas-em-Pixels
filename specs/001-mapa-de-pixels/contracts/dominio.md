# Contratos do domínio

APIs estáveis que a GUI e os testes devem honrar. Sem I/O de janela.

## geometria

```
Ponto(x: int, y: int)

Retangulo.de_dois_pontos(a: Ponto, b: Ponto) -> Retangulo
    Pré: nenhum
    Pós: largura >= 1, altura >= 1
         x == min(a.x, b.x), y == min(a.y, b.y)
         largura == abs(a.x - b.x) + 1
         de_dois_pontos(a,b) == de_dois_pontos(b,a)

Retangulo.intersecao(outro) -> Retangulo | None
    Pós: None se não há pixel em comum; senão o retângulo da
         sobreposição (também inclusivo).

Retangulo.contem_ponto(p: Ponto) -> bool
    x <= p.x < x+largura  AND  y <= p.y < y+altura
```

## regua

```
marcas_no_intervalo(inicio: int, tamanho: int, passo: int) -> list[int]
    Pré: passo > 0; tamanho pode ser <= 0 → lista vazia
    Pós: todos os itens são múltiplos de passo
         inicio <= item < inicio + tamanho
         lista crescente, sem duplicatas
```

## pagina

```
TAMANHOS_PAGINA: mapping nome -> (w_pt, h_pt)  # retrato nativo

pagina_em_pontos(tamanho: str, orientacao: str) -> (float, float)
    Erro: tamanho/orientação desconhecidos
    Retrato: largura <= altura
    Paisagem: largura >= altura
    A4 retrato ≈ 595.27 × 841.89

escala_para_caber(sw, sh, dw, dh) -> float
    Erro se sw<=0 ou sh<=0
    Pós: sw*s <= dw + 1e-6 AND sh*s <= dh + 1e-6
         s é o maior tal fator (min das duas razões)
```

## pdf.gerar_mapa_pdf

```
gerar_mapa_pdf(destino, retangulo, *, tamanho_pagina, orientacao,
               captura=None, titulo, origem_x, origem_y, metadados)
    -> Path

Pré: retangulo.largura >= 1 e altura >= 1
Pós: arquivo existe; começa com %PDF
     /MediaBox corresponde a pagina_em_pontos(...)
     captura, se houver, é desenhada antes da grade
```

## plataforma.listar_monitores (borda, mas contrato da GUI)

```
listar_monitores() -> list[Monitor]
    Pós: len >= 1 (sempre há fallback de um monitor)
         exatamente um primario=True se a fonte informar; senão o
         índice 0 é tratado como primário.
```
