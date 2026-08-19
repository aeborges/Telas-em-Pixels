"""Dica de coordenadas abaixo do cursor (atravessável, sem foco)."""

from __future__ import annotations

import tkinter as tk

from telas_em_pixels.plataforma.click_through import definir_atravessavel
from telas_em_pixels.plataforma.monitores import Monitor
from telas_em_pixels.ui import tema


class DicaCursor(tk.Toplevel):
    LARGURA = 168
    ALTURA = 32
    OFFSET_X = 14
    OFFSET_Y = 22

    def __init__(self, mestre: tk.Misc) -> None:
        super().__init__(mestre)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=tema.ACCENT)
        try:
            self.attributes("-transparentcolor", "#010101")
        except tk.TclError:
            pass

        self._texto = tk.StringVar(value="")
        moldura = tk.Frame(self, bg=tema.ACCENT, padx=1, pady=1)
        moldura.pack(fill="both", expand=True)
        inner = tk.Frame(moldura, bg="#1E2130")
        inner.pack(fill="both", expand=True)
        tk.Label(
            inner,
            textvariable=self._texto,
            bg="#1E2130",
            fg="#F5F5F8",
            font=tema.fonte(9, "bold"),
            padx=8,
            pady=4,
        ).pack()

        self._pronta = False
        self.withdraw()

    def atualizar(
        self,
        x_global: int,
        y_global: int,
        monitor: Monitor | None,
        visivel: bool,
    ) -> None:
        if not visivel:
            self.withdraw()
            return

        if monitor is None:
            texto = f"global {x_global}, {y_global}"
            local = None
        else:
            local = monitor.para_local(x_global, y_global)
            if local is None:
                texto = "fora do monitor"
            else:
                texto = f"x {local.x}   y {local.y}"

        self._texto.set(texto)
        dx, dy = self.OFFSET_X, self.OFFSET_Y
        if monitor is not None and local is not None:
            if local.x + dx + self.LARGURA > monitor.largura:
                dx = -self.LARGURA - 8
            if local.y + dy + self.ALTURA > monitor.altura:
                dy = -self.ALTURA - 12
        self.geometry(f"+{x_global + dx}+{y_global + dy}")
        if not self.winfo_viewable():
            self.deiconify()
            self.lift()
            self.update_idletasks()
            if not self._pronta:
                try:
                    definir_atravessavel(self, True)
                except Exception:
                    pass
                self._pronta = True
