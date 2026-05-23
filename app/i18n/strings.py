from __future__ import annotations


SUPPORTED_LANGS: tuple[str, ...] = ("zh", "ru")

LANG_GLYPH: dict[str, str] = {
    "zh": "文",
    "ru": "Я",
}


STRINGS: dict[str, dict[str, str]] = {
    # ===== top bar =====
    "top_bar.refresh_tooltip": {
        "zh": "重新扫描图像库 (Ctrl+R)",
        "ru": "Пересканировать библиотеку (Ctrl+R)",
    },
    "top_bar.theme.light": {"zh": "浅色", "ru": "Светлая"},
    "top_bar.theme.dark": {"zh": "深色", "ru": "Тёмная"},
    "top_bar.theme.system": {"zh": "跟随系统", "ru": "Системная"},
    "top_bar.theme_tooltip": {
        "zh": "切换主题 (Ctrl+T 循环切换)",
        "ru": "Сменить тему (Ctrl+T — циклически)",
    },
    "top_bar.language_tooltip": {"zh": "切换语言", "ru": "Сменить язык"},
    "top_bar.lang.zh": {"zh": "中文", "ru": "中文"},
    "top_bar.lang.ru": {"zh": "Русский", "ru": "Русский"},

    # ===== status bar =====
    "status.path_empty": {"zh": "—", "ru": "—"},
    "status.count": {"zh": "共 {n} 张", "ru": "Всего: {n}"},
    "status.zoom_empty": {"zh": "缩放 —", "ru": "Масштаб —"},
    "status.zoom": {"zh": "缩放 {percent:.0f}%", "ru": "Масштаб {percent:.0f}%"},
    "status.theme.light": {"zh": "浅色", "ru": "Светлая"},
    "status.theme.dark": {"zh": "深色", "ru": "Тёмная"},
    "status.theme.system": {
        "zh": "跟随系统 ({resolved})",
        "ru": "Системная ({resolved})",
    },

    # ===== filter panel =====
    "filter.section.lidar": {
        "zh": "激光雷达型号  ·  LIDAR",
        "ru": "Модель лидара  ·  LIDAR",
    },
    "filter.section.cloud": {
        "zh": "云类型  ·  CLOUD",
        "ru": "Тип облака  ·  CLOUD",
    },
    "filter.section.polarization": {
        "zh": "偏振方式  ·  POLARIZATION",
        "ru": "Поляризация  ·  POLARIZATION",
    },
    "filter.section.method": {
        "zh": "计算方法  ·  METHOD",
        "ru": "Метод  ·  METHOD",
    },
    "filter.section.thickness": {
        "zh": "云层厚度  ·  THICKNESS",
        "ru": "Толщина облака  ·  THICKNESS",
    },
    "filter.section.rfov": {
        "zh": "接收视场角  ·  rFOV",
        "ru": "Угол поля зрения  ·  rFOV",
    },
    "filter.section.data_type": {
        "zh": "数据类型  ·  DATA TYPE",
        "ru": "Тип данных  ·  DATA TYPE",
    },
    "filter.reset": {"zh": "重置", "ru": "Сбросить"},
    "filter.apply": {"zh": "应用筛选", "ru": "Применить фильтр"},

    # ===== mode switcher =====
    "mode.single": {"zh": "单图", "ru": "Одиночный"},
    "mode.grid": {"zh": "网格对比", "ru": "Сетка"},
    "mode.free": {"zh": "自由对比", "ru": "Свободный"},

    # ===== image card =====
    "card.unselected_dash": {
        "zh": "— 未选择图像 —",
        "ru": "— Изображение не выбрано —",
    },
    "card.fit": {"zh": "适应", "ru": "Вписать"},
    "card.unselected_title": {"zh": "未选择图像", "ru": "Изображение не выбрано"},
    "card.unselected_hint": {
        "zh": "请在左侧参数面板设置参数后点击应用",
        "ru": "Задайте параметры на панели слева и нажмите «Применить»",
    },
    "card.load_failed": {
        "zh": "加载失败: {name}",
        "ru": "Ошибка загрузки: {name}",
    },
    "card.zoom_tooltip": {
        "zh": "缩放百分比 (Enter 确认)",
        "ru": "Уровень масштаба (Enter — подтвердить)",
    },
    "card.zoom_in_tooltip": {"zh": "放大", "ru": "Увеличить"},
    "card.zoom_out_tooltip": {"zh": "缩小", "ru": "Уменьшить"},
    "card.fit_tooltip": {"zh": "适应窗口", "ru": "Вписать в окно"},

    # ===== views =====
    "view.no_match_hint": {
        "zh": "无匹配图像 — 请调整参数",
        "ru": "Нет совпадений — измените параметры",
    },
    "view.no_match_short": {"zh": "无匹配图像", "ru": "Нет совпадений"},
    "view.grid_label": {
        "zh": "{rows}×{cols} 网格",
        "ru": "Сетка {rows}×{cols}",
    },
    "view.free.add_panel": {"zh": "+ 新增面板", "ru": "+ Добавить панель"},
    "view.free.drag_hint": {
        "zh": "拖动面板间分割线调整大小  ·  点击 × 关闭面板",
        "ru": "Перетащите разделитель для изменения размера  ·  × — закрыть панель",
    },
    "view.free.title": {"zh": "自由模式", "ru": "Свободный режим"},

    # ===== grid preset =====
    "grid.preset_title": {"zh": "网格预设", "ru": "Шаблоны сетки"},
    "grid.sync_zoom": {"zh": "同步缩放", "ru": "Синхронный масштаб"},

    # ===== enums =====
    "enum.polarization.CIRC": {"zh": "圆偏振", "ru": "Круговая поляризация"},
    "enum.polarization.LINEAR": {"zh": "线偏振", "ru": "Линейная поляризация"},
    "enum.polarization.NONE": {"zh": "无偏振", "ru": "Без поляризации"},
    "enum.method.STANDARD": {"zh": "标准", "ru": "Стандартный"},
    "enum.method.ADAPTIVE": {"zh": "自适应", "ru": "Адаптивный"},
    "enum.method.MIXED": {"zh": "混合", "ru": "Смешанный"},
    "enum.data_type.ERROR_TOTAL": {"zh": "总误差", "ru": "Суммарная погрешность"},
    "enum.data_type.IQUV_I": {"zh": "强度 I", "ru": "Интенсивность I"},
    "enum.data_type.STOKES_DEPDEG": {
        "zh": "退偏度 DoLP",
        "ru": "Степень линейной поляризации DoLP",
    },
    "enum.data_type.STOKES_DOP": {
        "zh": "偏振度 DoP",
        "ru": "Степень поляризации DoP",
    },
    "enum.data_type.STOKES_PREANG": {
        "zh": "偏振角 PreAng",
        "ru": "Угол поляризации PreAng",
    },
    "enum.data_type.TOTAL_RETURN_SIGNAL": {
        "zh": "总回波信号",
        "ru": "Полный обратный сигнал",
    },
    "enum.rfov.default": {"zh": "默认", "ru": "По умолчанию"},

    # ===== dialogs =====
    "dialog.scan_title": {"zh": "扫描结果", "ru": "Результат сканирования"},
    "dialog.scan_empty": {
        "zh": "未在 {root} 下找到任何图片",
        "ru": "В {root} не найдено ни одного изображения",
    },
    "status.bootstrap_empty": {
        "zh": "未在 {root} 下找到任何图片  ·  请检查目录结构",
        "ru": "В {root} не найдено ни одного изображения  ·  проверьте структуру каталогов",
    },
}
