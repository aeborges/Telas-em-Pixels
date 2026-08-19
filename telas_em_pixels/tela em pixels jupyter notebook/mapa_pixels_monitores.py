"""Mapa de pixels para monitores - Windows 10/11.

Overlay transparente e click-through com regua, grade, coordenada do cursor,
selecao por dois pontos e exportacao vetorial para PDF.
"""
from __future__ import annotations

import ctypes
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Deve ocorrer antes de criar QApplication, para usar coordenadas fisicas por monitor.
if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

from PySide6.QtCore import QPoint, QRect, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QPainter, QPageLayout, QPageSize, QPen, QPdfWriter
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget
)


@dataclass
class Selection:
    first: QPoint | None = None
    second: QPoint | None = None

    def rectangle(self) -> QRect | None:
        if self.first is None or self.second is None:
            return None
        return QRect(self.first, self.second).normalized()


class Overlay(QWidget):
    selection_changed = Signal(object)
    selection_finished = Signal(object)

    def __init__(self):
        super().__init__()
        self.major = 100
        self.minor = 10
        self.opacity_pct = 70
        self.selection = Selection()
        self.selecting = False
        self.monitor_rect = QRect()
        self.setWindowTitle("Mapa de pixels - overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self._set_click_through(True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def set_monitor(self, rect: QRect):
        self.monitor_rect = QRect(rect)
        self.setGeometry(rect)
        self.selection = Selection()
        self.update()

    def _set_click_through(self, enabled: bool):
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, enabled)
        try:
            self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enabled)
            if self.isVisible():
                self.show()
        except Exception:
            pass
        if sys.platform == "win32" and self.winId():
            hwnd = int(self.winId())
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_NOACTIVATE = 0x08000000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= WS_EX_LAYERED | WS_EX_NOACTIVATE
            style = (style | WS_EX_TRANSPARENT) if enabled else (style & ~WS_EX_TRANSPARENT)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    def begin_selection(self):
        self.selection = Selection()
        self.selecting = True
        self._set_click_through(False)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.activateWindow()
        self.raise_()
        self.update()

    def cancel_selection(self):
        self.selecting = False
        self.selection = Selection()
        self.unsetCursor()
        self._set_click_through(True)
        self.selection_changed.emit(None)
        self.update()

    def mousePressEvent(self, event):
        if not self.selecting or event.button() != Qt.MouseButton.LeftButton:
            return
        p = event.position().toPoint()
        if self.selection.first is None:
            self.selection.first = p
            self.selection.second = p
        else:
            self.selection.second = p
            rect = self.selection.rectangle()
            self.selecting = False
            self.unsetCursor()
            self._set_click_through(True)
            self.selection_changed.emit(rect)
            self.selection_finished.emit(rect)
        self.update()

    def mouseMoveEvent(self, event):
        if self.selecting and self.selection.first is not None:
            self.selection.second = event.position().toPoint()
            self.selection_changed.emit(self.selection.rectangle())
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_selection()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        alpha = max(20, min(255, round(self.opacity_pct * 2.55)))
        minor_pen = QPen(QColor(30, 160, 220, int(alpha * 0.35)), 1)
        major_pen = QPen(QColor(0, 110, 190, alpha), 1)
        text_color = QColor(0, 80, 140, alpha)
        w, h = self.width(), self.height()

        # Grade: linhas de 10 px, reforco e rotulo a cada 100 px.
        for x in range(0, w + 1, self.minor):
            major = x % self.major == 0
            p.setPen(major_pen if major else minor_pen)
            tick = 15 if major else (8 if x % 50 == 0 else 4)
            p.drawLine(x, 0, x, h if major else tick)
            if major and x > 0:
                p.setPen(text_color)
                p.drawText(x + 3, 15, str(x))
        for y in range(0, h + 1, self.minor):
            major = y % self.major == 0
            p.setPen(major_pen if major else minor_pen)
            tick = 15 if major else (8 if y % 50 == 0 else 4)
            p.drawLine(0, y, w if major else tick, y)
            if major and y > 0:
                p.setPen(text_color)
                p.drawText(3, y - 3, str(y))

        # Coordenada do cursor, local no monitor e global no desktop virtual.
        global_pos = QCursor.pos()
        local = self.mapFromGlobal(global_pos)
        if self.rect().contains(local):
            label = f"x={local.x()} px  y={local.y()} px | global {global_pos.x()}, {global_pos.y()}"
            font = QFont("Segoe UI", 9)
            p.setFont(font)
            fm = p.fontMetrics()
            box = fm.boundingRect(label).adjusted(-6, -4, 6, 4)
            pos = local + QPoint(14, 20)
            if pos.x() + box.width() > w:
                pos.setX(max(0, local.x() - box.width() - 14))
            if pos.y() + box.height() > h:
                pos.setY(max(0, local.y() - box.height() - 14))
            box.moveTopLeft(pos)
            p.fillRect(box, QColor(20, 20, 20, 210))
            p.setPen(QColor(255, 255, 255))
            p.drawText(box.adjusted(6, 4, -6, -4), Qt.AlignmentFlag.AlignLeft, label)

        rect = self.selection.rectangle()
        if rect and rect.width() > 0 and rect.height() > 0:
            p.fillRect(rect, QColor(255, 190, 0, 35))
            p.setPen(QPen(QColor(220, 80, 0, 230), 2, Qt.PenStyle.DashLine))
            p.drawRect(rect)
            p.setPen(QColor(130, 30, 0))
            p.drawText(rect.topLeft() + QPoint(5, 16), f"{rect.width()} x {rect.height()} px")


class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa de pixels dos monitores")
        self.overlay = Overlay()
        self.screens = QApplication.screens()

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        form = QFormLayout()
        self.monitor_combo = QComboBox()
        for i, screen in enumerate(self.screens, 1):
            g = screen.geometry()
            self.monitor_combo.addItem(
                f"Monitor {i}: {screen.name()} | {g.width()} x {g.height()} | origem {g.x()}, {g.y()}"
            )
        form.addRow("Monitor:", self.monitor_combo)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(10, 100)
        self.opacity_spin.setValue(70)
        self.opacity_spin.setSuffix(" %")
        form.addRow("Opacidade da grade:", self.opacity_spin)

        self.orientation = QComboBox()
        self.orientation.addItems(["Automatica", "Portrait", "Landscape"])
        form.addRow("Orientacao do PDF:", self.orientation)
        layout.addLayout(form)

        row = QHBoxLayout()
        self.toggle_btn = QPushButton("Ocultar mapa")
        self.select_btn = QPushButton("Selecionar por 2 pontos")
        self.full_btn = QPushButton("Usar tela inteira")
        row.addWidget(self.toggle_btn)
        row.addWidget(self.select_btn)
        row.addWidget(self.full_btn)
        layout.addLayout(row)

        self.status = QLabel("Overlay ativo e permeavel a cliques.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.export_btn = QPushButton("Gerar PDF da area definida")
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.current_selection: QRect | None = None
        self.monitor_combo.currentIndexChanged.connect(self.apply_monitor)
        self.opacity_spin.valueChanged.connect(self.change_opacity)
        self.toggle_btn.clicked.connect(self.toggle_overlay)
        self.select_btn.clicked.connect(self.start_selection)
        self.full_btn.clicked.connect(self.use_full_screen)
        self.export_btn.clicked.connect(self.export_pdf)
        self.overlay.selection_changed.connect(self.selection_changed)
        self.overlay.selection_finished.connect(self.selection_finished)

        self.resize(680, 230)
        self.apply_monitor(0)
        self.overlay.show()

    def apply_monitor(self, index):
        screen = self.screens[index]
        self.overlay.set_monitor(screen.geometry())
        self.current_selection = None
        self.export_btn.setEnabled(False)
        self.status.setText("Overlay ativo e permeavel a cliques.")

    def change_opacity(self, value):
        self.overlay.opacity_pct = value
        self.overlay.update()

    def toggle_overlay(self):
        if self.overlay.isVisible():
            self.overlay.hide()
            self.toggle_btn.setText("Mostrar mapa")
        else:
            self.overlay.show()
            self.overlay.raise_()
            self.toggle_btn.setText("Ocultar mapa")

    def start_selection(self):
        if not self.overlay.isVisible():
            self.overlay.show()
        self.status.setText("Clique no primeiro canto e depois no canto oposto. Esc cancela.")
        self.overlay.begin_selection()

    def use_full_screen(self):
        self.current_selection = QRect(0, 0, self.overlay.width(), self.overlay.height())
        self.overlay.selection.first = self.current_selection.topLeft()
        self.overlay.selection.second = self.current_selection.bottomRight()
        self.overlay.update()
        self.export_btn.setEnabled(True)
        self.status.setText(
            f"Tela inteira: {self.current_selection.width()} x {self.current_selection.height()} px."
        )

    def selection_changed(self, rect):
        if rect:
            self.status.setText(
                f"Area: x={rect.x()}, y={rect.y()}, {rect.width()} x {rect.height()} px."
            )

    def selection_finished(self, rect):
        if rect and rect.width() >= 2 and rect.height() >= 2:
            self.current_selection = rect
            self.export_btn.setEnabled(True)
        else:
            self.current_selection = None
            self.export_btn.setEnabled(False)
            self.status.setText("Selecao muito pequena. Repita a operacao.")

    @staticmethod
    def nice_step(span: int, target_lines: int = 12) -> int:
        raw = max(1.0, span / target_lines)
        power = 10 ** math.floor(math.log10(raw))
        for factor in (1, 2, 5, 10):
            step = factor * power
            if step >= raw:
                return int(step)
        return int(10 * power)

    def export_pdf(self):
        rect = self.current_selection
        if not rect:
            return
        default_name = f"mapa_pixels_{rect.width()}x{rect.height()}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Salvar mapa em PDF", default_name, "PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        selected = self.orientation.currentText()
        if selected == "Automatica":
            selected = "Landscape" if rect.width() >= rect.height() else "Portrait"
        orientation = (
            QPageLayout.Orientation.Landscape
            if selected == "Landscape" else QPageLayout.Orientation.Portrait
        )

        writer = QPdfWriter(path)
        writer.setTitle("Mapa de pixels da tela")
        writer.setCreator("Mapa de pixels dos monitores")
        writer.setResolution(300)
        layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4), orientation,
            QPageLayout.MarginsF(10, 10, 10, 10), QPageLayout.Unit.Millimeter
        )
        writer.setPageLayout(layout)

        painter = QPainter(writer)
        page = writer.pageLayout().paintRectPixels(writer.resolution())
        margin = 90
        title_h = 150
        target = QRectF(page.left() + margin, page.top() + title_h,
                        page.width() - 2 * margin, page.height() - title_h - margin)
        scale = min(target.width() / rect.width(), target.height() / rect.height())
        draw_w, draw_h = rect.width() * scale, rect.height() * scale
        plot = QRectF(target.center().x() - draw_w / 2, target.center().y() - draw_h / 2, draw_w, draw_h)

        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.setPen(QColor(20, 20, 20))
        painter.drawText(QRectF(page.left() + margin, page.top() + 20, page.width() - 2 * margin, 50),
                         Qt.AlignmentFlag.AlignLeft, "Mapa de pixels da selecao")
        painter.setFont(QFont("Segoe UI", 8))
        global_origin = self.overlay.mapToGlobal(rect.topLeft())
        subtitle = (f"Selecao local: ({rect.x()}, {rect.y()}) ate ({rect.right()}, {rect.bottom()}) | "
                    f"dimensoes: {rect.width()} x {rect.height()} px | "
                    f"origem global: ({global_origin.x()}, {global_origin.y()})")
        painter.drawText(QRectF(page.left() + margin, page.top() + 70, page.width() - 2 * margin, 60),
                         Qt.TextFlag.TextWordWrap, subtitle)

        xstep = self.nice_step(rect.width())
        ystep = self.nice_step(rect.height())
        painter.fillRect(plot, QColor(250, 252, 254))
        painter.setFont(QFont("Segoe UI", 7))

        # Linhas no sistema de coordenadas local da selecao; rotulos absolutos no monitor.
        x = 0
        while x <= rect.width():
            px = plot.left() + x * scale
            major = x % (xstep * 5) == 0
            painter.setPen(QPen(QColor(80, 130, 170, 180 if major else 90), 1))
            painter.drawLine(QPoint(int(px), int(plot.top())), QPoint(int(px), int(plot.bottom())))
            painter.setPen(QColor(20, 70, 110))
            painter.drawText(QRectF(px + 2, plot.top() + 2, 90, 20), str(rect.x() + x))
            x += xstep
        y = 0
        while y <= rect.height():
            py = plot.top() + y * scale
            major = y % (ystep * 5) == 0
            painter.setPen(QPen(QColor(80, 130, 170, 180 if major else 90), 1))
            painter.drawLine(QPoint(int(plot.left()), int(py)), QPoint(int(plot.right()), int(py)))
            painter.setPen(QColor(20, 70, 110))
            painter.drawText(QRectF(plot.left() + 2, py + 2, 90, 20), str(rect.y() + y))
            y += ystep
        painter.setPen(QPen(QColor(0, 70, 120), 2))
        painter.drawRect(plot)
        painter.end()

        if Path(path).exists() and Path(path).stat().st_size > 0:
            self.status.setText(f"PDF gerado: {os.path.abspath(path)}")
            QMessageBox.information(self, "PDF gerado", f"Arquivo salvo em:\n{os.path.abspath(path)}")
        else:
            QMessageBox.critical(self, "Falha", "O PDF nao foi gerado corretamente.")

    def closeEvent(self, event):
        self.overlay.close()
        event.accept()


def main():
    if sys.platform != "win32":
        print("Este aplicativo foi projetado para Windows 10/11.")
    app = QApplication(sys.argv)
    app.setApplicationName("Mapa de pixels dos monitores")
    panel = ControlPanel()
    panel.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
