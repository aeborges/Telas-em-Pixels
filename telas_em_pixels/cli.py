"""Entrada de linha de comando (GUI só é importada se for abrir a janela)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from telas_em_pixels.dominio.demo import gerar_demo_pdf


def analisar_argv(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="telas-em-pixels",
        description="Mapa de pixels (régua) dos monitores, com exportação PDF.",
    )
    parser.add_argument(
        "--demo-pdf",
        metavar="ARQUIVO",
        help="Gera um PDF de demonstração e encerra (sem GUI).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = analisar_argv(argv)
    if args.demo_pdf:
        gerar_demo_pdf(Path(args.demo_pdf))
        return 0
    from telas_em_pixels.app import Aplicativo

    app = Aplicativo()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
