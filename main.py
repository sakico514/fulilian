from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

# When bundled by PyInstaller, files are in sys._MEIPASS
if getattr(sys, "frozen", False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(__file__)

# Try bundled .env first, then local .env (allows overriding)
load_dotenv(os.path.join(base_dir, ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

from PyQt6.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    from pet_window import PetWindow

    pet = PetWindow()
    pet.move(100, 100)
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
