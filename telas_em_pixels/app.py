"""Aplicativo: coordenadas ao vivo, região por clique/digitação e mapa."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from telas_em_pixels.dominio.geometria import Ponto, Retangulo
from telas_em_pixels.dominio.pdf import gerar_mapa_pdf
from telas_em_pixels.plataforma.captura import capturar_retangulo
from telas_em_pixels.plataforma.dpi import aplicar_dpi_awareness, area_util_tela
from telas_em_pixels.plataforma.monitores import Monitor, listar_monitores
from telas_em_pixels.plataforma.ponteiro import (
    botao_esquerdo_pressionado,
    posicao_cursor,
    tecla_escape_pressionada,
)
from telas_em_pixels.ui.mapa import CanvasMapa
from telas_em_pixels.ui.painel import PainelControle
from telas_em_pixels.ui import tema

_INTERVALO_MS = 16


class Aplicativo(tk.Tk):
    def __init__(self) -> None:
        aplicar_dpi_awareness()
        super().__init__()
        self.title("Telas em Pixels — mapa de pixels")
        self.configure(bg=tema.BG_APP)
        self.resizable(True, True)
        self._aplicar_geometria_inicial()
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
            ao_atualizar_mapa=self._atualizar_mapa,
            ao_capturar=self._iniciar_captura,
            ao_usar_monitor=self._usar_monitor_inteiro,
            ao_pdf_monitor=self._pdf_monitor,
            ao_pdf_selecao=self._pdf_selecao,
        )
        self.painel.configure(width=560)
        self.painel.pack(side="left", fill="y")
        self.painel.pack_propagate(False)
        self.painel.coluna_direita.pack(side="left", fill="both", expand=True)
        self.mapa = CanvasMapa(self.painel.area_mapa)
        self.mapa.pack(fill="both", expand=True, padx=(4, 12), pady=(8, 12))
        self.painel.definir_monitores(self.monitores, primario)

        self._ultima_selecao: tuple[Retangulo, Retangulo] | None = None
        self._modo_captura: str | None = None  # "a" | "b" | "dois"
        self._captura_passo = 0
        self._esperando_soltar = False
        self._atualizando = False
        self._foto_regiao = None
        self._regiao_foto: Retangulo | None = None

        self.bind_all("<Escape>", lambda _e: self._cancelar_captura())
        self.bind_all("<F8>", lambda _e: self._capturar_f8())
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self.after(_INTERVALO_MS, self._tick_ponteiro)

    @property
    def monitor(self) -> Monitor:
        return self.monitores[self.indice_monitor]

    def _aplicar_geometria_inicial(self) -> None:
        """Abre a janela dentro da área útil, sem estourar a tela."""
        alvo_w, alvo_h = 1280, 680
        ax, ay, aw, ah = area_util_tela()
        if aw < 1 or ah < 1:
            aw = max(int(self.winfo_screenwidth()), alvo_w)
            ah = max(int(self.winfo_screenheight()), alvo_h)
            ax, ay = 0, 0
        margem = 12
        w = min(alvo_w, max(960, aw - margem))
        h = min(alvo_h, max(560, ah - margem))
        w = min(w, aw - margem)
        h = min(h, ah - margem)
        x = ax + max(0, (aw - w) // 2)
        y = ay + max(0, min(16, ah - h))
        if y + h > ay + ah:
            y = ay
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(min(960, w), min(560, h))

    def _tick_ponteiro(self) -> None:
        try:
            gx, gy = self._ler_ponteiro()
        except tk.TclError:
            return
        local = self.monitor.para_local(gx, gy)
        self.painel.atualizar_ponteiro(gx, gy, local)
        self.mapa.atualizar_ponteiro(local)
        self._processar_captura(gx, gy)
        self.after(_INTERVALO_MS, self._tick_ponteiro)

    def _ler_ponteiro(self) -> tuple[int, int]:
        pos = posicao_cursor()
        if pos is not None:
            return pos
        return int(self.winfo_pointerx()), int(self.winfo_pointery())

    def _sobre_esta_janela(self, gx: int, gy: int) -> bool:
        x, y = self.winfo_rootx(), self.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        return x <= gx < x + w and y <= gy < y + h

    def _iniciar_captura(self, modo: str) -> None:
        if modo == "dois":
            self.painel.limpar_pontos()
        self._modo_captura = modo
        self._captura_passo = 0
        self._esperando_soltar = botao_esquerdo_pressionado()
        if modo == "dois":
            self.painel.status(
                "Aponte o primeiro canto e pressione F8 (ou clique fora desta "
                "janela). Esc cancela."
            )
        else:
            qual = "A" if modo == "a" else "B"
            self.painel.status(
                f"Aponte o ponto {qual} e pressione F8 (ou clique fora desta "
                "janela). Esc cancela."
            )

    def _cancelar_captura(self) -> None:
        if self._modo_captura is None:
            return
        self._modo_captura = None
        self.painel.status("Captura cancelada.")

    def _capturar_f8(self) -> None:
        gx, gy = self._ler_ponteiro()
        if self._modo_captura is None:
            self._modo_captura = "b" if self.painel.ponto_a_ok() else "a"
        self._registrar_ponto(gx, gy)

    def _processar_captura(self, gx: int, gy: int) -> None:
        if self._modo_captura is None:
            return
        if tecla_escape_pressionada():
            self._cancelar_captura()
            return
        pressionado = botao_esquerdo_pressionado()
        if self._esperando_soltar:
            if not pressionado:
                self._esperando_soltar = False
            return
        if pressionado and not self._sobre_esta_janela(gx, gy):
            self._registrar_ponto(gx, gy)
            self._esperando_soltar = True

    def _registrar_ponto(self, gx: int, gy: int) -> None:
        modo = self._modo_captura
        if modo is None:
            return
        local = self.monitor.para_local(gx, gy)
        if local is None:
            local = Ponto(gx - self.monitor.x, gy - self.monitor.y)
            self.painel.status(
                f"Ponto ({local.x}, {local.y}) está fora do monitor — "
                "ajuste ou escolha outro monitor."
            )
        if modo == "a":
            self.painel.definir_ponto("a", local)
            self._modo_captura = None
            self.painel.status(f"Ponto A: ({local.x}, {local.y}).")
        elif modo == "b":
            self.painel.definir_ponto("b", local)
            self._modo_captura = None
            self.painel.status(f"Ponto B: ({local.x}, {local.y}).")
        else:
            if self._captura_passo == 0:
                self.painel.definir_ponto("a", local)
                self._captura_passo = 1
                self.painel.status(
                    f"Ponto A: ({local.x}, {local.y}). Agora o segundo canto "
                    "(F8 ou clique)."
                )
            else:
                self.painel.definir_ponto("b", local)
                self._modo_captura = None
                self.painel.status(f"Ponto B: ({local.x}, {local.y}). Mapa gerado.")

    def _trocar_monitor(self, indice: int) -> None:
        self.indice_monitor = indice
        self._descartar_ultima_selecao()
        self._foto_regiao = None
        self._regiao_foto = None
        self.painel.status(f"Monitor: {self.monitor.rotulo}.")
        self._atualizar_mapa()

    def _usar_monitor_inteiro(self) -> None:
        mon = self.monitor
        self.painel.definir_pontos(
            Ponto(0, 0), Ponto(mon.largura - 1, mon.altura - 1)
        )
        self.painel.status(
            f"Região = monitor inteiro ({mon.largura}×{mon.altura} px)."
        )

    def _atualizar_mapa(self) -> None:
        if self._atualizando:
            return
        self._atualizando = True
        try:
            pontos = self.painel.pontos_locais()
            if pontos is None:
                self.mapa.mostrar(None, self.painel.estilo_grade())
                self._descartar_ultima_selecao()
                return
            a, b = pontos
            local = Retangulo.de_dois_pontos(a, b)
            recorte = self.monitor.retangulo.traduzir(
                -self.monitor.x, -self.monitor.y
            )
            local_clip = recorte.intersecao(local)
            if local_clip is None:
                self.mapa.mostrar(None, self.painel.estilo_grade())
                self._descartar_ultima_selecao()
                self.painel.status("A região não cruza o monitor selecionado.")
                return
            global_recortado = local_clip.traduzir(self.monitor.x, self.monitor.y)
            estilo = self.painel.estilo_grade()
            captura = None
            if self.painel.captura_var.get():
                if self._regiao_foto != global_recortado:
                    captura = capturar_retangulo(global_recortado)
                    self._foto_regiao = captura
                    self._regiao_foto = global_recortado
                else:
                    captura = self._foto_regiao
            else:
                self._foto_regiao = None
                self._regiao_foto = None
            self.mapa.mostrar(local_clip, estilo, captura)
            self._ultima_selecao = (global_recortado, local_clip)
            self.painel.habilitar_pdf_selecao(True)
        except ValueError:
            self.mapa.mostrar(None, self.painel.estilo_grade())
            self._descartar_ultima_selecao()
        finally:
            self._atualizando = False

    def _descartar_ultima_selecao(self) -> None:
        self._ultima_selecao = None
        self.painel.habilitar_pdf_selecao(False)

    def _pdf_selecao(self) -> None:
        if self._ultima_selecao is None:
            return
        global_recortado, local = self._ultima_selecao
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

        incluir_captura = self.painel.captura_var.get()
        if incluir_captura:
            self.withdraw()
            self.update_idletasks()
        self.after(
            120 if incluir_captura else 10,
            lambda: self._gravar_pdf(
                caminho, ret_global, ret_local, titulo, incluir_captura
            ),
        )

    def _gravar_pdf(
        self,
        caminho: str,
        ret_global: Retangulo,
        ret_local: Retangulo,
        titulo: str,
        incluir_captura: bool,
    ) -> None:
        captura = None
        if incluir_captura:
            captura = capturar_retangulo(ret_global)
            if captura is None:
                self.painel.status(
                    "Não foi possível capturar a tela; o PDF sairá só com a grade."
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
                estilo=self.painel.estilo_grade(),
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
        if incluir_captura:
            try:
                self.deiconify()
                self.lift()
            except tk.TclError:
                pass

    def _ao_fechar(self) -> None:
        self.destroy()
