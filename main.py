from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.theme.theme_manager import ThemeManager


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
