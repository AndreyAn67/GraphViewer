from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.theme.theme_manager import ThemeManager


# When frozen by PyInstaller, sys.executable is the .exe; the image library
# lives in a `sources/pics/` folder shipped *next to* the exe so it stays
# browsable/updatable. In a normal dev run, resolve relative to this file.
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent
PICS_ROOT = PROJECT_ROOT / "sources" / "pics"


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("GraphViewer")
    app.setOrganizationName("GraphViewer")

    theme = ThemeManager(app)
    theme.apply("dark")

    window = MainWindow(pics_root=PICS_ROOT, theme=theme)
    window.resize(1440, 900)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
