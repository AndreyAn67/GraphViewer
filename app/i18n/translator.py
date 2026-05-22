from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.i18n.strings import STRINGS, SUPPORTED_LANGS


class Translator(QObject):
    """Runtime language switcher.

    Mirrors the shape of ThemeManager: holds the current language code,
    emits `languageChanged(str)` when set_language() actually changes it,
    and exposes `tr(key, **kwargs)` for catalog lookup with str.format.
    """

    languageChanged = Signal(str)

    def __init__(self, default: str = "zh") -> None:
        super().__init__()
        self._current: str = default if default in SUPPORTED_LANGS else "zh"

    @property
    def current(self) -> str:
        return self._current

    def set_language(self, lang: str) -> None:
        if lang not in SUPPORTED_LANGS:
            return
        if lang == self._current:
            return
        self._current = lang
        self.languageChanged.emit(lang)

    def tr(self, key: str, **kwargs) -> str:
        entry = STRINGS.get(key)
        if entry is None:
            return key
        text = entry.get(self._current) or entry.get("zh") or key
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return text
        return text
