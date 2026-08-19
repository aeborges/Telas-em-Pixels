"""Integração: --demo-pdf gera arquivo válido."""

from pathlib import Path

from telas_em_pixels.cli import main
from telas_em_pixels.dominio.demo import gerar_demo_pdf


def test_gerar_demo_pdf(tmp_path: Path):
    dest = tmp_path / "demo.pdf"
    saida = gerar_demo_pdf(dest)
    assert saida == dest
    data = dest.read_bytes()
    assert data.startswith(b"%PDF")
    assert dest.stat().st_size > 2000


def test_main_demo_pdf(tmp_path: Path):
    dest = tmp_path / "via-main.pdf"
    assert main(["--demo-pdf", str(dest)]) == 0
    assert dest.is_file()
    assert dest.read_bytes()[:4] == b"%PDF"
