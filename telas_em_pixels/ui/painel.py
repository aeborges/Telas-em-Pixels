"""Painel de controle: ponteiro, região, grade e PDF."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import colorchooser, ttk

from telas_em_pixels.dominio.geometria import Ponto
from telas_em_pixels.dominio.pagina import ORIENTACOES, TAMANHOS_PAGINA
from telas_em_pixels.dominio.regua import (
    COR_PRINCIPAL_PADRAO,
    COR_SECUNDARIA_PADRAO,
    EstiloGrade,
    normalizar_cor_hex,
)
from telas_em_pixels.plataforma.monitores import Monitor
from telas_em_pixels.ui import tema


class PainelControle(tk.Frame):
    def __init__(
        self,
        mestre: tk.Misc,
        *,
        ao_trocar_monitor: Callable[[int], None],
        ao_atualizar_mapa: Callable[[], None],
        ao_capturar: Callable[[str], None],
        ao_usar_monitor: Callable[[], None],
        ao_pdf_monitor: Callable[[], None],
        ao_pdf_selecao: Callable[[], None],
    ) -> None:
        super().__init__(mestre, bg=tema.BG_APP)
        self._ao_trocar_monitor = ao_trocar_monitor
        self._ao_atualizar_mapa = ao_atualizar_mapa
        self._ao_capturar = ao_capturar
        self._monitores: list[Monitor] = []
        self._silencio = False

        self.monitor_var = tk.StringVar()
        self.captura_var = tk.BooleanVar(value=True)
        self.tamanho_var = tk.StringVar(value="A4")
        self.orientacao_var = tk.StringVar(value="paisagem")
        self.status_var = tk.StringVar(
            value="Ponteiro ao vivo. Defina dois pontos para gerar o mapa."
        )
        self.ponteiro_var = tk.StringVar(value="x  —      y  —")
        self.ponteiro_local_var = tk.StringVar(value="Aguardando o ponteiro…")

        self.x1_var = tk.StringVar()
        self.y1_var = tk.StringVar()
        self.x2_var = tk.StringVar()
        self.y2_var = tk.StringVar()
        self.passo_maior_var = tk.StringVar(value="100")
        self.passo_menor_var = tk.StringVar(value="10")
        self.cor_principal_var = tk.StringVar(value=COR_PRINCIPAL_PADRAO)
        self.cor_secundaria_var = tk.StringVar(value=COR_SECUNDARIA_PADRAO)

        self._montar()
        self._combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._emitir_monitor(),
        )
        self.btn_pdf.configure(command=ao_pdf_monitor)
        self.btn_sel.configure(command=lambda: ao_capturar("dois"))
        self.btn_pdf_sel.configure(command=ao_pdf_selecao)
        self.btn_monitor.configure(command=ao_usar_monitor)
        self.btn_pt_a.configure(command=lambda: ao_capturar("a"))
        self.btn_pt_b.configure(command=lambda: ao_capturar("b"))
        for var in (
            self.x1_var,
            self.y1_var,
            self.x2_var,
            self.y2_var,
            self.passo_maior_var,
            self.passo_menor_var,
        ):
            var.trace_add("write", lambda *_: self._emitir_mapa())
        self.captura_var.trace_add("write", lambda *_: self._emitir_mapa())

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
        estilo.configure(
            "Ponteiro.TLabel",
            background=tema.BG_TOOLBAR,
            foreground=tema.TEXT,
            font=tema.fonte(16, "bold"),
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
            text="Coordenadas ao vivo e mapa de pixels da região que você definir.",
            background=tema.BG_APP,
            foreground=tema.TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(0, 8))

        self._card_ponteiro()
        self._card_monitor_regiao()
        self._card_grade()
        self._card_pdf()

        rodape = tk.Frame(self, bg=tema.BG_APP)
        rodape.pack(fill="x", side="bottom")
        tk.Label(
            rodape,
            textvariable=self.status_var,
            bg=tema.BG_APP,
            fg=tema.TEXT_MUTED,
            font=tema.fonte(8),
            wraplength=460,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=16, pady=(4, 10))

        assert set(ORIENTACOES) == {"retrato", "paisagem"}

    def _card(self) -> ttk.Frame:
        borda = tk.Frame(
            self,
            bg=tema.BG_TOOLBAR,
            highlightbackground=tema.BORDER,
            highlightthickness=1,
        )
        borda.pack(fill="x", padx=16, pady=4)
        inner = ttk.Frame(borda, padding=10, style="Card.TFrame")
        inner.pack(fill="x")
        return inner

    def _card_ponteiro(self) -> None:
        inner = self._card()
        ttk.Label(inner, text="Ponteiro", style="Card.TLabel").pack(anchor="w")
        ttk.Label(
            inner, textvariable=self.ponteiro_var, style="Ponteiro.TLabel"
        ).pack(anchor="w", pady=(4, 0))
        ttk.Label(
            inner, textvariable=self.ponteiro_local_var, style="Muted.TLabel"
        ).pack(anchor="w", pady=(2, 0))

    def _card_monitor_regiao(self) -> None:
        inner = self._card()
        ttk.Label(inner, text="Monitor e região", style="Card.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w"
        )
        self._combo = ttk.Combobox(
            inner,
            textvariable=self.monitor_var,
            state="readonly",
            width=42,
        )
        self._combo.grid(
            row=1, column=0, columnspan=4, sticky="ew", pady=(4, 8)
        )

        ttk.Label(inner, text="Ponto A (x, y do monitor)", style="Muted.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(inner, text="Ponto B (x, y do monitor)", style="Muted.TLabel").grid(
            row=2, column=2, columnspan=2, sticky="w", padx=(12, 0)
        )
        self._entry(inner, self.x1_var).grid(row=3, column=0, sticky="ew")
        self._entry(inner, self.y1_var).grid(
            row=3, column=1, sticky="ew", padx=(4, 0)
        )
        self._entry(inner, self.x2_var).grid(
            row=3, column=2, sticky="ew", padx=(12, 0)
        )
        self._entry(inner, self.y2_var).grid(
            row=3, column=3, sticky="ew", padx=(4, 0)
        )

        self.btn_pt_a = ttk.Button(inner, text="Clicar ponto A")
        self.btn_pt_a.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.btn_pt_b = ttk.Button(inner, text="Clicar ponto B")
        self.btn_pt_b.grid(
            row=4, column=2, columnspan=2, sticky="ew", pady=(8, 0), padx=(12, 0)
        )
        self.btn_sel = ttk.Button(inner, text="Clicar dois cantos na tela (F8)")
        self.btn_sel.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        self.btn_monitor = ttk.Button(inner, text="Usar o monitor inteiro")
        self.btn_monitor.grid(
            row=6, column=0, columnspan=4, sticky="ew", pady=(6, 0)
        )
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(2, weight=1)
        inner.columnconfigure(3, weight=1)

    def _card_grade(self) -> None:
        inner = self._card()
        ttk.Label(inner, text="Grade de pixels", style="Card.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w"
        )
        ttk.Label(
            inner, text="Linhas principais (px)", style="Muted.TLabel"
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(
            inner, text="Linhas secundárias (px)", style="Muted.TLabel"
        ).grid(row=1, column=2, columnspan=2, sticky="w", pady=(8, 0), padx=(12, 0))

        sp_maior = ttk.Spinbox(
            inner,
            from_=2,
            to=2000,
            increment=10,
            textvariable=self.passo_maior_var,
            width=8,
        )
        sp_maior.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 8))
        sp_menor = ttk.Spinbox(
            inner,
            from_=1,
            to=500,
            increment=5,
            textvariable=self.passo_menor_var,
            width=8,
        )
        sp_menor.grid(
            row=2, column=2, columnspan=2, sticky="w", pady=(2, 8), padx=(12, 0)
        )

        ttk.Label(inner, text="Cor principal", style="Muted.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(inner, text="Cor secundária", style="Muted.TLabel").grid(
            row=3, column=2, columnspan=2, sticky="w", padx=(12, 0)
        )

        self.btn_cor_pri = tk.Label(
            inner,
            text=COR_PRINCIPAL_PADRAO,
            bg=COR_PRINCIPAL_PADRAO,
            fg="#1E2130",
            relief="solid",
            bd=1,
            cursor="hand2",
        )
        self.btn_cor_pri.grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(2, 6)
        )
        self.btn_cor_pri.bind(
            "<Button-1>", lambda _e: self._escolher_cor("principal")
        )
        self.btn_cor_sec = tk.Label(
            inner,
            text=COR_SECUNDARIA_PADRAO,
            bg=COR_SECUNDARIA_PADRAO,
            fg="#1E2130",
            relief="solid",
            bd=1,
            cursor="hand2",
        )
        self.btn_cor_sec.grid(
            row=4, column=2, columnspan=2, sticky="ew", pady=(2, 6), padx=(12, 0)
        )
        self.btn_cor_sec.bind(
            "<Button-1>", lambda _e: self._escolher_cor("secundaria")
        )

        ttk.Button(
            inner,
            text="Tons padrão  cinza 74 / 84",
            command=self._aplicar_cinzas_padrao,
        ).grid(row=5, column=0, columnspan=4, sticky="ew")
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(2, weight=1)

    def _card_pdf(self) -> None:
        inner = self._card()
        ttk.Label(inner, text="Geração de PDF", style="Card.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(inner, text="Tamanho da página", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Combobox(
            inner,
            textvariable=self.tamanho_var,
            values=list(TAMANHOS_PAGINA.keys()),
            state="readonly",
            width=12,
        ).grid(row=2, column=0, sticky="w", pady=(2, 8))

        ttk.Label(inner, text="Orientação", style="Muted.TLabel").grid(
            row=1, column=1, sticky="w", pady=(8, 0), padx=(16, 0)
        )
        oris = ttk.Frame(inner, style="Card.TFrame")
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
            inner,
            text="Incluir captura da tela no mapa e no PDF",
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
            inner, text="Gerar PDF do monitor inteiro", style="Accent.TButton"
        )
        self.btn_pdf.grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)
        self.btn_pdf_sel = ttk.Button(
            inner, text="Gerar PDF da seleção", state="disabled"
        )
        self.btn_pdf_sel.grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

    def _entry(self, pai: tk.Misc, var: tk.StringVar) -> ttk.Entry:
        return ttk.Entry(pai, textvariable=var, width=8)

    def _escolher_cor(self, qual: str) -> None:
        atual = (
            self.cor_principal_var.get()
            if qual == "principal"
            else self.cor_secundaria_var.get()
        )
        _rgb, hex_cor = colorchooser.askcolor(
            color=atual, title="Cor da grade", parent=self.winfo_toplevel()
        )
        if not hex_cor:
            return
        try:
            hex_cor = normalizar_cor_hex(hex_cor)
        except ValueError:
            return
        if qual == "principal":
            self.cor_principal_var.set(hex_cor)
            self.btn_cor_pri.configure(text=hex_cor, bg=hex_cor)
        else:
            self.cor_secundaria_var.set(hex_cor)
            self.btn_cor_sec.configure(text=hex_cor, bg=hex_cor)
        self._ao_atualizar_mapa()

    def _aplicar_cinzas_padrao(self) -> None:
        self.cor_principal_var.set(COR_PRINCIPAL_PADRAO)
        self.cor_secundaria_var.set(COR_SECUNDARIA_PADRAO)
        self.btn_cor_pri.configure(text=COR_PRINCIPAL_PADRAO, bg=COR_PRINCIPAL_PADRAO)
        self.btn_cor_sec.configure(
            text=COR_SECUNDARIA_PADRAO, bg=COR_SECUNDARIA_PADRAO
        )
        self._ao_atualizar_mapa()

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

    def habilitar_pdf_selecao(self, ligado: bool) -> None:
        self.btn_pdf_sel.configure(state="normal" if ligado else "disabled")

    def atualizar_ponteiro(
        self, x_global: int, y_global: int, local: Ponto | None
    ) -> None:
        self.ponteiro_var.set(f"x  {x_global}      y  {y_global}")
        if local is None:
            self.ponteiro_local_var.set("Fora do monitor selecionado")
        else:
            self.ponteiro_local_var.set(
                f"No monitor:  x {local.x}   y {local.y}"
            )

    def definir_ponto(self, qual: str, ponto: Ponto) -> None:
        self._silencio = True
        try:
            if qual == "a":
                self.x1_var.set(str(ponto.x))
                self.y1_var.set(str(ponto.y))
            else:
                self.x2_var.set(str(ponto.x))
                self.y2_var.set(str(ponto.y))
        finally:
            self._silencio = False
        self._emitir_mapa()

    def definir_pontos(self, a: Ponto, b: Ponto) -> None:
        self._silencio = True
        try:
            self.x1_var.set(str(a.x))
            self.y1_var.set(str(a.y))
            self.x2_var.set(str(b.x))
            self.y2_var.set(str(b.y))
        finally:
            self._silencio = False
        self._emitir_mapa()

    def limpar_pontos(self) -> None:
        self._silencio = True
        try:
            self.x1_var.set("")
            self.y1_var.set("")
            self.x2_var.set("")
            self.y2_var.set("")
        finally:
            self._silencio = False
        self._emitir_mapa()

    def ponto_a_ok(self) -> bool:
        try:
            int(self.x1_var.get())
            int(self.y1_var.get())
        except ValueError:
            return False
        return True

    def _emitir_mapa(self) -> None:
        if not self._silencio:
            self._ao_atualizar_mapa()

    def pontos_locais(self) -> tuple[Ponto, Ponto] | None:
        try:
            a = Ponto(int(self.x1_var.get()), int(self.y1_var.get()))
            b = Ponto(int(self.x2_var.get()), int(self.y2_var.get()))
        except ValueError:
            return None
        return a, b

    def estilo_grade(self) -> EstiloGrade:
        try:
            maior = int(self.passo_maior_var.get())
            menor = int(self.passo_menor_var.get())
        except ValueError:
            maior, menor = 100, 10
        maior = max(1, maior)
        menor = max(1, menor)
        try:
            return EstiloGrade(
                passo_menor=menor,
                passo_maior=maior,
                cor_principal=self.cor_principal_var.get(),
                cor_secundaria=self.cor_secundaria_var.get(),
            )
        except ValueError:
            return EstiloGrade()

    def _emitir_monitor(self) -> None:
        self._ao_trocar_monitor(self.indice_monitor())
