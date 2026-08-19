"""Overlay de régua sobre um monitor, atravessável no modo normal."""

from __future__ import annotations

import sys
import tkinter as tk
from collections.abc import Callable

from telas_em_pixels.dominio.geometria import Ponto, Retangulo
from telas_em_pixels.dominio.regua import EspecificacaoRegua
from telas_em_pixels.plataforma.click_through import definir_atravessavel
from telas_em_pixels.plataforma.monitores import Monitor
from telas_em_pixels.ui import tema


class OverlayMapa(tk.Toplevel):
    def __init__(self, mestre: tk.Misc) -> None:
        super().__init__(mestre)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        if sys.platform == "win32":
            fundo = tema.CHROMA
        else:
            fundo = "#0E1018"
        self.configure(bg=fundo)
        if sys.platform == "win32":
            try:
                self.attributes("-transparentcolor", tema.CHROMA)
            except tk.TclError:
                pass
        else:
            try:
                self.attributes("-alpha", 0.38)
            except tk.TclError:
                pass

        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0,
            bg=fundo,
            cursor="crosshair",
        )
        self.canvas.pack(fill="both", expand=True)

        self._monitor: Monitor | None = None
        self._atravessavel = True
        self._selecionando = False
        self._primeiro: Ponto | None = None
        self._ao_concluir: Callable[[Ponto, Ponto], None] | None = None
        self._ao_cancelar: Callable[[], None] | None = None
        self._spec = EspecificacaoRegua()

        self.canvas.bind("<Button-1>", self._no_clique)
        self.canvas.bind("<Motion>", self._no_movimento)
        self.bind("<Escape>", lambda _e: self.cancelar_selecao())

    def cobrir(self, monitor: Monitor) -> None:
        self._monitor = monitor
        self.geometry(
            f"{monitor.largura}x{monitor.altura}+{monitor.x}+{monitor.y}"
        )
        self.deiconify()
        self.lift()
        self.update_idletasks()
        self._desenhar_regua()
        if not self._selecionando:
            self._aplicar_atravessavel(True)

    def ocultar(self) -> None:
        self.withdraw()

    def visivel(self) -> bool:
        try:
            return bool(self.winfo_viewable())
        except tk.TclError:
            return False

    def iniciar_selecao(
        self,
        ao_concluir: Callable[[Ponto, Ponto], None],
        ao_cancelar: Callable[[], None],
    ) -> None:
        self._ao_concluir = ao_concluir
        self._ao_cancelar = ao_cancelar
        self._primeiro = None
        self._selecionando = True
        self.canvas.delete("elastico")
        if self._monitor is not None:
            self.cobrir(self._monitor)
        self._aplicar_atravessavel(False)
        self.lift()
        try:
            self.focus_force()
        except tk.TclError:
            pass

    def cancelar_selecao(self) -> None:
        if not self._selecionando:
            return
        self._encerrar_selecao()
        if self._ao_cancelar:
            self._ao_cancelar()

    def _encerrar_selecao(self) -> None:
        self._selecionando = False
        self._primeiro = None
        self.canvas.delete("elastico")
        self._aplicar_atravessavel(True)

    def _aplicar_atravessavel(self, valor: bool) -> None:
        self._atravessavel = valor
        try:
            definir_atravessavel(self, valor)
        except Exception:
            pass

    def _desenhar_regua(self) -> None:
        self.canvas.delete("regua")
        if self._monitor is None:
            return
        w, h = self._monitor.largura, self._monitor.altura
        spec = self._spec
        c = self.canvas

        def haste(x1: int, y1: int, x2: int, y2: int) -> None:
            c.create_line(
                x1 + 1,
                y1 + 1,
                x2 + 1,
                y2 + 1,
                fill=tema.COR_TICK_CLARO,
                width=1,
                tags="regua",
            )
            c.create_line(
                x1, y1, x2, y2, fill=tema.COR_TICK, width=1, tags="regua"
            )

        for x in spec.maiores(0, w):
            haste(x, 0, x, h)
            c.create_text(
                x + 4,
                16,
                text=str(x),
                anchor="nw",
                fill=tema.COR_TICK,
                font=tema.fonte(8, "bold"),
                tags="regua",
            )
        for y in spec.maiores(0, h):
            if y == 0:
                continue
            haste(0, y, w, y)
            c.create_text(
                6,
                y + 4,
                text=str(y),
                anchor="nw",
                fill=tema.COR_TICK,
                font=tema.fonte(8, "bold"),
                tags="regua",
            )

        for x in spec.menores(0, w):
            tam = 14 if x % spec.passo_maior == 0 else 7
            haste(x, 0, x, tam)
            haste(x, h - tam, x, h)
        for y in spec.menores(0, h):
            tam = 14 if y % spec.passo_maior == 0 else 7
            haste(0, y, tam, y)
            haste(w - tam, y, w, y)

        c.create_text(
            8,
            2,
            text="0,0",
            anchor="nw",
            fill=tema.ACCENT,
            font=tema.fonte(8, "bold"),
            tags="regua",
        )

    def _no_clique(self, evento: tk.Event) -> None:
        if not self._selecionando:
            return
        ponto = Ponto(int(evento.x_root), int(evento.y_root))
        if self._primeiro is None:
            self._primeiro = ponto
            return
        p1, p2 = self._primeiro, ponto
        self._encerrar_selecao()
        if self._ao_concluir:
            self._ao_concluir(p1, p2)

    def _no_movimento(self, evento: tk.Event) -> None:
        if not self._selecionando or self._primeiro is None:
            return
        a = self._primeiro
        b = Ponto(int(evento.x_root), int(evento.y_root))
        ret = Retangulo.de_dois_pontos(a, b)
        if self._monitor is None:
            return
        x = ret.x - self._monitor.x
        y = ret.y - self._monitor.y
        self.canvas.delete("elastico")
        self.canvas.create_rectangle(
            x,
            y,
            x + ret.largura,
            y + ret.altura,
            outline=tema.COR_ELASTICO,
            width=2,
            tags="elastico",
        )
        self.canvas.create_text(
            x + 8,
            y + 8,
            text=f"{ret.largura}×{ret.altura} px",
            anchor="nw",
            fill=tema.COR_ELASTICO,
            font=tema.fonte(9, "bold"),
            tags="elastico",
        )
