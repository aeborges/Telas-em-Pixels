"""
Lançador sem console (Windows associa .pyw ao pythonw.exe automaticamente).

Clique duas vezes neste arquivo para abrir o app sem a janela preta do
terminal. Para depurar com saída de erro visível, rode `python main.py`.
"""

from telas_em_pixels.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
