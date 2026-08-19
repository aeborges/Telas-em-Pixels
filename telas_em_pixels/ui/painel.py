"""Painel de controle — a única janela que captura interação contínua."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from telas_em_pixels.dominio.pagina import ORIENTACOES, TAMANHOS_PAGINA
from telas_em_pixels.plataforma.monitores import Monitor
from telas_em_pixels.ui import tema


class PainelControle(tk.Frame):
    def __init__(
        self,
        mestre: tk.Misc,
        *,
        ao_trocar_monitor: Callable[[int], None],
        ao_toggle_mapa: Callable[[bool], None],
        ao_toggle_dica: Callable[[bool], None],
        ao_pdf_monitor: Callable[[], None],
        ao_selecionar: Callable[[], None],
    ) -> None:
        super().__init__(mestre, bg=tema.BG_APP)
        self._ao_trocar_monitor = ao_trocar_monitor
        self._monitores: list[Monitor] = []

        self.monitor_var = tk.StringVar()
        self.mapa_var = tk.BooleanVar(value=True)
        self.dica_var = tk.BooleanVar(value=True)
        self.captura_var = tk.BooleanVar(value=True)
        self.tamanho_var = tk.StringVar(value="A4")
        self.orientacao_var = tk.StringVar(value="paisagem")
        self.status_var = tk.StringVar(
            value="Mapa pronto — cliques passam através do overlay."
        )

        self._montar()
        self._combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._emitir_monitor(),
        )
        self.chk_mapa.configure(
            command=lambda: ao_toggle_mapa(self.mapa_var.get())
        )
        self.chk_dica.configure(
            command=lambda: ao_toggle_dica(self.dica_var.get())
        )
        self.btn_pdf.configure(command=ao_pdf_monitor)
        self.btn_sel.configure(command=ao_selecionar)

    def _montar(self) -> None:
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("TFrame", background=tema.BG_APP)
        estilo.configure("Card.TFrame", background=tema.BG_TOOLBAR)
        estilo.configure(
            "TLabel", background=tema.BG_APP, foreground=tema.TEXT
        )
        estilo.configure(
            "Card.TLabel",
            background=tema.BG_TOOLBAR,
            foreground=tema.TEXT,
        )
        estilo.configure(
            "Muted.TLabel",
            background=tema.BG_TOOLBAR,
            foreground=tema.TEXT_MUTED,
        )
        estilo.configure(
            "Titulo.TLabel",
            background=tema.BG_APP,
            foreground=tema.TEXT,
            font=tema.fonte(13, "bold"),
        )
        estilo.configure("TCheckbutton", background=tema.BG_TOOLBAR)
        estilo.configure(
            "Accent.TButton",
            background=tema.ACCENT,
            foreground="#FFFFFF",
            padding=8,
        )
        estilo.map("Accent.TButton", background=[("active", "#4A4ED9")])

        pad = {"padx": 16, "pady": (12, 4)}
        ttk.Label(self, text="Telas em Pixels", style="Titulo.TLabel").pack(
            anchor="w", **pad
        )
        ttk.Label(
            self,
            text="Mapa-régua sobre o monitor, sem bloquear a tela.",
            background=tema.BG_APP,
            foreground=tema.TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(0, 10))

        card = tk.Frame(
            self,
            bg=tema.BG_TOOLBAR,
            highlightbackground=tema.BORDER,
            highlightthickness=1,
        )
        card.pack(fill="x", padx=16, pady=6)
        inner = ttk.Frame(card, padding=12, style="Card.TFrame")
        inner.pack(fill="x")

        ttk.Label(inner, text="Monitor", style="Card.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self._combo = ttk.Combobox(
            inner,
            textvariable=self.monitor_var,
            state="readonly",
            width=36,
        )
        self._combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 10))

        self.chk_mapa = tk.Checkbutton(
            inner,
            text="Mostrar mapa de pixels (régua 10 / 100 px)",
            variable=self.mapa_var,
            bg=tema.BG_TOOLBAR,
            fg=tema.TEXT,
            activebackground=tema.BG_TOOLBAR,
            selectcolor=tema.BG_TOOLBAR,
            font=tema.fonte(9),
            anchor="w",
        )
        self.chk_mapa.grid(row=2, column=0, columnspan=2, sticky="w")

        self.chk_dica = tk.Checkbutton(
            inner,
            text="Dica de coordenadas abaixo do cursor",
            variable=self.dica_var,
            bg=tema.BG_TOOLBAR,
            fg=tema.TEXT,
            activebackground=tema.BG_TOOLBAR,
            selectcolor=tema.BG_TOOLBAR,
            font=tema.fonte(9),
            anchor="w",
        )
        self.chk_dica.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 0))
        inner.columnconfigure(0, weight=1)

        pdf = tk.Frame(
            self,
            bg=tema.BG_TOOLBAR,
            highlightbackground=tema.BORDER,
            highlightthickness=1,
        )
        pdf.pack(fill="x", padx=16, pady=6)
        pinner = ttk.Frame(pdf, padding=12, style="Card.TFrame")
        pinner.pack(fill="x")
        ttk.Label(
            pinner, text="Geração de PDF", style="Card.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(pinner, text="Tamanho da página", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Combobox(
            pinner,
            textvariable=self.tamanho_var,
            values=list(TAMANHOS_PAGINA.keys()),
            state="readonly",
            width=12,
        ).grid(row=2, column=0, sticky="w", pady=(2, 8))

        ttk.Label(pinner, text="Orientação", style="Muted.TLabel").grid(
            row=1, column=1, sticky="w", pady=(8, 0), padx=(16, 0)
        )
        oris = ttk.Frame(pinner, style="Card.TFrame")
        oris.grid(row=2, column=1, sticky="w", padx=(16, 0))
        for valor, rotulo in (("retrato", "Retrato"), ("paisagem", "Paisagem")):
            tk.Radiobutton(
                oris,
                text=rotulo,
                value=valor,
                variable=self.orientacao_var,
                bg=tema.BG_TOOLBAR,
                fg=tema.TEXT,
                activebackground=tema.BG_TOOLBAR,
                selectcolor=tema.BG_TOOLBAR,
                font=tema.fonte(9),
            ).pack(side="left", padx=(0, 10))

        self.chk_cap = tk.Checkbutton(
            pinner,
            text="Incluir captura da tela (sem o overlay) no PDF",
            variable=self.captura_var,
            bg=tema.BG_TOOLBAR,
            fg=tema.TEXT,
            activebackground=tema.BG_TOOLBAR,
            selectcolor=tema.BG_TOOLBAR,
            font=tema.fonte(9),
            anchor="w",
        )
        self.chk_cap.grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 10))

        self.btn_pdf = ttk.Button(
            pinner, text="Gerar PDF do monitor inteiro", style="Accent.TButton"
        )
        self.btn_pdf.grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)
        self.btn_sel = ttk.Button(
            pinner, text="Selecionar região (dois pontos na tela)"
        )
        self.btn_sel.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        pinner.columnconfigure(0, weight=1)
        pinner.columnconfigure(1, weight=1)

        ajuda = tk.Frame(self, bg=tema.BG_APP)
        ajuda.pack(fill="x", padx=16, pady=(8, 0))
        tk.Label(
            ajuda,
            text="No modo normal o mapa não come cliques. Durante a seleção "
            "de região, clique dois pontos (qualquer ordem). Esc cancela.",
            bg=tema.BG_APP,
            fg=tema.TEXT_MUTED,
            font=tema.fonte(8),
            wraplength=400,
            justify="left",
            anchor="w",
        ).pack(fill="x")

        rodape = tk.Frame(self, bg=tema.BG_APP)
        rodape.pack(fill="x", side="bottom")
        tk.Label(
            rodape,
            textvariable=self.status_var,
            bg=tema.BG_APP,
            fg=tema.TEXT_MUTED,
            font=tema.fonte(8),
            wraplength=400,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=16, pady=(6, 12))

        # silêncio de linter: ORIENTACOES documenta o contrato
        assert set(ORIENTACOES) == {"retrato", "paisagem"}

    def definir_monitores(self, monitores: list[Monitor], indice: int = 0) -> None:
        self._monitores = monitores
        rotulos = [m.rotulo for m in monitores]
        self._combo.configure(values=rotulos)
        if rotulos:
            indice = max(0, min(indice, len(rotulos) - 1))
            self.monitor_var.set(rotulos[indice])
        self._combo.configure(state="readonly" if len(rotulos) > 1 else "disabled")

    def indice_monitor(self) -> int:
        rotulo = self.monitor_var.get()
        for i, m in enumerate(self._monitores):
            if m.rotulo == rotulo:
                return i
        return 0

    def status(self, texto: str) -> None:
        self.status_var.set(texto)

    def _emitir_monitor(self) -> None:
        self._ao_trocar_monitor(self.indice_monitor())
