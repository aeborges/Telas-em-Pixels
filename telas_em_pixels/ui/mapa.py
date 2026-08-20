"""Canvas com o mapa de pixels da região definida."""

from __future__ import annotations

import tkinter as tk
from typing import Any

from telas_em_pixels.dominio.geometria import Ponto, Retangulo
from telas_em_pixels.dominio.regua import EstiloGrade
from telas_em_pixels.ui import tema


class CanvasMapa(tk.Frame):
    """Desenha a grade da região (e, se houver, a captura como fundo)."""

    def __init__(self, mestre: tk.Misc) -> None:
        super().__init__(mestre, bg=tema.BG_APP)
        tk.Label(
            self,
            text="Mapa de pixels",
            bg=tema.BG_APP,
            fg=tema.TEXT,
            font=tema.fonte(11, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        self.canvas = tk.Canvas(
            self,
            bg="#FAFAFA",
            highlightthickness=1,
            highlightbackground=tema.BORDER,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._regiao: Retangulo | None = None
        self._estilo = EstiloGrade()
        self._foto: Any = None
        self._escala = 1.0
        self._ox = 0.0
        self._oy = 0.0
        self._placeholder = (
            "Defina a região digitando dois pontos ou clicando na tela "
            "(F8 captura a posição do ponteiro)."
        )
        self.canvas.bind("<Configure>", lambda _e: self.redesenhar())
        self.redesenhar()

    def definir_placeholder(self, texto: str) -> None:
        self._placeholder = texto
        if self._regiao is None:
            self.redesenhar()

    def mostrar(
        self,
        regiao: Retangulo | None,
        estilo: EstiloGrade,
        captura: Any | None = None,
    ) -> None:
        self._regiao = regiao
        self._estilo = estilo
        self._foto = None
        if captura is not None and regiao is not None:
            self._foto = captura
        self.redesenhar()

    def atualizar_ponteiro(self, local: Ponto | None) -> None:
        self.canvas.delete("ponteiro")
        if local is None or self._regiao is None:
            return
        if not self._regiao.contem_ponto(local):
            return
        x, y = self._para_canvas(local.x, local.y)
        r = 5
        self.canvas.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            outline=tema.ACCENT,
            width=2,
            tags="ponteiro",
        )
        self.canvas.create_line(
            x - 10,
            y,
            x + 10,
            y,
            fill=tema.ACCENT,
            width=1,
            tags="ponteiro",
        )
        self.canvas.create_line(
            x,
            y - 10,
            x,
            y + 10,
            fill=tema.ACCENT,
            width=1,
            tags="ponteiro",
        )

    def redesenhar(self) -> None:
        c = self.canvas
        c.delete("mapa")
        c.delete("ponteiro")
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        if self._regiao is None:
            c.create_text(
                w / 2,
                h / 2,
                text=self._placeholder,
                fill=tema.TEXT_MUTED,
                font=tema.fonte(9),
                width=max(w - 32, 80),
                justify="center",
                tags="mapa",
            )
            return

        ret = self._regiao
        estilo = self._estilo
        spec = estilo.spec
        margem_esq = 36
        margem_sup = 22
        margem_dir = 10
        margem_inf = 10
        area_w = max(1.0, w - margem_esq - margem_dir)
        area_h = max(1.0, h - margem_sup - margem_inf)
        escala = min(area_w / ret.largura, area_h / ret.altura)
        mapa_w = ret.largura * escala
        mapa_h = ret.altura * escala
        ox = margem_esq + (area_w - mapa_w) / 2
        oy = margem_sup + (area_h - mapa_h) / 2
        self._escala = escala
        self._ox = ox
        self._oy = oy

        fundo = self._imagem_fundo(int(mapa_w), int(mapa_h))
        if fundo is not None:
            c.create_image(ox, oy, image=fundo, anchor="nw", tags="mapa")
        else:
            c.create_rectangle(
                ox,
                oy,
                ox + mapa_w,
                oy + mapa_h,
                fill="#FFFFFF",
                outline="",
                tags="mapa",
            )

        ox1, oy1 = ox + mapa_w, oy + mapa_h
        menores_x = spec.menores(ret.x, ret.largura)
        menores_y = spec.menores(ret.y, ret.altura)
        maiores_x = set(spec.maiores(ret.x, ret.largura))
        maiores_y = set(spec.maiores(ret.y, ret.altura))

        # Secundárias: mais finas e mais claras
        if escala * spec.passo_menor >= 2.0:
            for mx in menores_x:
                if mx in maiores_x:
                    continue
                px = self._para_canvas(mx, ret.y)[0]
                c.create_line(
                    px,
                    oy,
                    px,
                    oy1,
                    fill=estilo.cor_secundaria,
                    width=1,
                    tags="mapa",
                )
            for my in menores_y:
                if my in maiores_y:
                    continue
                py = self._para_canvas(ret.x, my)[1]
                c.create_line(
                    ox,
                    py,
                    ox1,
                    py,
                    fill=estilo.cor_secundaria,
                    width=1,
                    tags="mapa",
                )

        # Principais: mais escuras (e um pouco mais grossas)
        for mx in spec.maiores(ret.x, ret.largura):
            px = self._para_canvas(mx, ret.y)[0]
            c.create_line(
                px,
                oy,
                px,
                oy1,
                fill=estilo.cor_principal,
                width=2,
                tags="mapa",
            )
            c.create_text(
                px,
                oy - 4,
                text=str(mx),
                anchor="s",
                fill=tema.TEXT,
                font=tema.fonte(7, "bold"),
                tags="mapa",
            )
        for my in spec.maiores(ret.y, ret.altura):
            py = self._para_canvas(ret.x, my)[1]
            c.create_line(
                ox,
                py,
                ox1,
                py,
                fill=estilo.cor_principal,
                width=2,
                tags="mapa",
            )
            if my != ret.y:
                c.create_text(
                    ox - 4,
                    py,
                    text=str(my),
                    anchor="e",
                    fill=tema.TEXT,
                    font=tema.fonte(7, "bold"),
                    tags="mapa",
                )

        c.create_rectangle(
            ox,
            oy,
            ox1,
            oy1,
            outline=tema.TEXT,
            width=1,
            tags="mapa",
        )
        c.create_text(
            ox + 4,
            oy1 - 4,
            text=f"{ret.largura}×{ret.altura} px",
            anchor="sw",
            fill=tema.TEXT_MUTED,
            font=tema.fonte(8),
            tags="mapa",
        )

    def _para_canvas(self, x_local: int, y_local: int) -> tuple[float, float]:
        assert self._regiao is not None
        return (
            self._ox + (x_local - self._regiao.x) * self._escala,
            self._oy + (y_local - self._regiao.y) * self._escala,
        )

    def _imagem_fundo(self, w: int, h: int) -> Any:
        if self._foto is None or w < 2 or h < 2:
            return None
        try:
            from PIL import ImageTk
        except Exception:
            return None
        try:
            redim = self._foto.resize((w, h))
            self._tk_fundo = ImageTk.PhotoImage(redim)
            return self._tk_fundo
        except Exception:
            return None
