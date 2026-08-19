"""Aplicativo: painel + overlay + dica + exportação PDF."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from telas_em_pixels.dominio.geometria import Ponto, Retangulo
from telas_em_pixels.dominio.pdf import gerar_mapa_pdf
from telas_em_pixels.plataforma.captura import capturar_retangulo
from telas_em_pixels.plataforma.dpi import aplicar_dpi_awareness
from telas_em_pixels.plataforma.monitores import Monitor, listar_monitores
from telas_em_pixels.ui.dica import DicaCursor
from telas_em_pixels.ui.overlay import OverlayMapa
from telas_em_pixels.ui.painel import PainelControle
from telas_em_pixels.ui import tema


class Aplicativo(tk.Tk):
    def __init__(self) -> None:
        aplicar_dpi_awareness()
        super().__init__()
        self.title("Telas em Pixels — mapa de pixels")
        self.geometry("460x620")
        self.minsize(420, 560)
        self.configure(bg=tema.BG_APP)
        self.resizable(False, True)
        try:
            self.attributes("-topmost", True)
        except tk.TclError:
            pass

        self.monitores: list[Monitor] = listar_monitores(self)
        primario = next((i for i, m in enumerate(self.monitores) if m.primario), 0)
        self.indice_monitor = primario

        self.painel = PainelControle(
            self,
            ao_trocar_monitor=self._trocar_monitor,
            ao_toggle_mapa=self._toggle_mapa,
            ao_toggle_dica=self._toggle_dica,
            ao_pdf_monitor=self._pdf_monitor,
            ao_selecionar=self._iniciar_selecao,
        )
        self.painel.pack(fill="both", expand=True)
        self.painel.definir_monitores(self.monitores, primario)

        self.overlay = OverlayMapa(self)
        self.dica = DicaCursor(self)
        self._tick_id: str | None = None

        self.bind("<Escape>", lambda _e: self.overlay.cancelar_selecao())
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self.after(80, self._iniciar_overlay)

    @property
    def monitor(self) -> Monitor:
        return self.monitores[self.indice_monitor]

    def _iniciar_overlay(self) -> None:
        if self.painel.mapa_var.get():
            self.overlay.cobrir(self.monitor)
            self.lift()
            self.painel.status(
                f"Mapa no {self.monitor.rotulo}. Cliques atravessam o overlay."
            )
        self._agendar_tick()

    def _agendar_tick(self) -> None:
        if self._tick_id is not None:
            try:
                self.after_cancel(self._tick_id)
            except Exception:
                pass
        self._tick_id = self.after(16, self._tick_cursor)

    def _tick_cursor(self) -> None:
        self._tick_id = None
        try:
            x = int(self.winfo_pointerx())
            y = int(self.winfo_pointery())
        except tk.TclError:
            return
        mostrar = (
            self.painel.dica_var.get()
            and self.painel.mapa_var.get()
            and self.overlay.visivel()
        )
        self.dica.atualizar(x, y, self.monitor, mostrar)
        self._agendar_tick()

    def _trocar_monitor(self, indice: int) -> None:
        self.indice_monitor = indice
        if self.painel.mapa_var.get():
            self.overlay.cobrir(self.monitor)
            self.lift()
            self.painel.status(f"Mapa no {self.monitor.rotulo}.")

    def _toggle_mapa(self, ligado: bool) -> None:
        if ligado:
            self.overlay.cobrir(self.monitor)
            self.lift()
            self.painel.status(f"Mapa no {self.monitor.rotulo}.")
        else:
            self.overlay.ocultar()
            self.dica.withdraw()
            self.painel.status("Mapa oculto. O painel continua disponível.")

    def _toggle_dica(self, ligado: bool) -> None:
        if not ligado:
            self.dica.withdraw()
            self.painel.status("Dica de coordenadas desligada.")
        else:
            self.painel.status("Dica de coordenadas ligada.")

    def _iniciar_selecao(self) -> None:
        if not self.painel.mapa_var.get():
            self.painel.mapa_var.set(True)
            self.overlay.cobrir(self.monitor)
        self.overlay.iniciar_selecao(self._selecao_pronta, self._selecao_cancelada)
        self.painel.status(
            "Clique o primeiro ponto da região no monitor mapeado. Esc cancela."
        )

    def _selecao_cancelada(self) -> None:
        self.painel.status("Seleção cancelada. Overlay atravessável de novo.")

    def _selecao_pronta(self, a: Ponto, b: Ponto) -> None:
        ret_global = Retangulo.de_dois_pontos(a, b)
        local = self.monitor.recortar_local(ret_global)
        if local is None:
            messagebox.showwarning(
                "Região fora do monitor",
                "Os dois pontos não cruzam o monitor selecionado.",
                parent=self,
            )
            self.painel.status("Seleção ignorada — fora do monitor ativo.")
            return
        global_recortado = local.traduzir(self.monitor.x, self.monitor.y)
        self.painel.status(
            f"Região {local.largura}×{local.altura} px em "
            f"({local.x}, {local.y}). Escolha onde salvar o PDF."
        )
        self._gerar_pdf(
            ret_global=global_recortado,
            ret_local=local,
            titulo=f"Mapa de pixels — seleção {local.largura}×{local.altura} px",
        )

    def _pdf_monitor(self) -> None:
        mon = self.monitor
        local = Retangulo(0, 0, mon.largura, mon.altura)
        self._gerar_pdf(
            ret_global=mon.retangulo,
            ret_local=local,
            titulo=f"Mapa de pixels — {mon.rotulo}",
        )

    def _gerar_pdf(
        self,
        *,
        ret_global: Retangulo,
        ret_local: Retangulo,
        titulo: str,
    ) -> None:
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar mapa de pixels em PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="mapa-de-pixels.pdf",
        )
        if not caminho:
            self.painel.status("Gravação de PDF cancelada.")
            return

        overlay_ligado = self.painel.mapa_var.get()
        self.overlay.ocultar()
        self.dica.withdraw()
        self.update_idletasks()
        self.after(
            120,
            lambda: self._gravar_pdf(
                caminho, ret_global, ret_local, titulo, overlay_ligado
            ),
        )

    def _gravar_pdf(
        self,
        caminho: str,
        ret_global: Retangulo,
        ret_local: Retangulo,
        titulo: str,
        restaurar_overlay: bool,
    ) -> None:
        captura = None
        if self.painel.captura_var.get():
            captura = capturar_retangulo(ret_global)
            if captura is None:
                self.painel.status(
                    "Não foi possível capturar a tela; o PDF sairá só com a régua."
                )
        try:
            gerar_mapa_pdf(
                caminho,
                ret_local,
                tamanho_pagina=self.painel.tamanho_var.get(),
                orientacao=self.painel.orientacao_var.get(),
                captura=captura,
                titulo=titulo,
                origem_x=ret_local.x,
                origem_y=ret_local.y,
                metadados={"monitor": self.monitor.rotulo},
            )
        except Exception as exc:
            messagebox.showerror(
                "Falha ao gerar PDF",
                f"Não foi possível gravar o arquivo:\n{exc}",
                parent=self,
            )
            self.painel.status("Falha ao gravar o PDF.")
        else:
            self.painel.status(f"PDF salvo em {caminho}")
        if restaurar_overlay:
            self.overlay.cobrir(self.monitor)
            self.lift()

    def _ao_fechar(self) -> None:
        try:
            self.overlay.destroy()
        except Exception:
            pass
        try:
            self.dica.destroy()
        except Exception:
            pass
        self.destroy()
