"""系统托盘图标模块"""
import threading
import pystray
from PIL import Image, ImageDraw
import tkinter as tk

from .styles import COLORS


class SystemTray:
    """系统托盘管理器"""

    _instance = None
    _icon = None
    _running = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._main_window = None
            self._on_quit_callback = None

    def create_icon(self):
        """创建托盘图标"""
        # 创建图标图像
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 画圆形背景
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=COLORS["primary"]
        )

        # 画勾号
        center = size // 2
        points = [
            (center - 12, center),
            (center - 4, center + 10),
            (center + 14, center - 8)
        ]
        draw.line(points + [points[0]], fill="white", width=5)

        return image

    def setup(self, main_window, on_quit=None):
        """设置托盘
        main_window: 主窗口 Frame（MainWindow实例），会自动找到其父窗口Tk
        """
        self._main_window = main_window
        self._on_quit_callback = on_quit

    def _create_menu(self):
        """创建右键菜单"""
        menu = pystray.Menu(
            pystray.MenuItem(
                '显示/隐藏窗口',
                self._toggle_window,
                default=True  # 双击图标时触发
            ),
            pystray.MenuItem(
                '退出',
                self._quit
            )
        )
        return menu

    def _get_root_window(self):
        """获取顶层窗口"""
        window = self._main_window
        while window and hasattr(window, 'master') and window.master:
            window = window.master
        return window

    def _toggle_window(self, icon=None, item=None):
        """切换窗口显示/隐藏"""
        window = self._get_root_window()
        if window:
            if window.winfo_viewable():
                window.withdraw()
            else:
                window.deiconify()
                window.lift()
                window.focus_force()

    def _show_window(self, icon=None, item=None):
        """显示主窗口"""
        window = self._get_root_window()
        if window:
            window.deiconify()
            window.lift()
            window.focus_force()

    def _quit(self, icon=None, item=None):
        """退出程序"""
        self._running = False
        if self._on_quit_callback:
            self._on_quit_callback()
        if self._icon:
            self._icon.stop()

    def run(self):
        """运行托盘图标"""
        if self._running:
            return

        self._running = True
        image = self.create_icon()
        menu = self._create_menu()

        self._icon = pystray.Icon(
            "TodoX",
            image,
            "TodoX - 待办事项",
            menu
        )

        # 在单独线程中运行
        def run_icon():
            self._icon.run()

        icon_thread = threading.Thread(target=run_icon, daemon=True)
        icon_thread.start()

    def stop(self):
        """停止托盘"""
        self._running = False
        if self._icon:
            self._icon.stop()


class HiddenRoot(tk.Tk):
    """隐藏的根窗口，用于保持程序运行"""

    def __init__(self, tray):
        super().__init__()
        self.withdraw()  # 隐藏窗口
        self.tray = tray

        # 窗口关闭时最小化到托盘而不是退出
        self.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

    def _minimize_to_tray(self):
        """最小化到托盘"""
        self.withdraw()
        if not self.tray._running:
            self.tray.run()


def create_tray_with_hidden_window(main_window_class, on_quit=None):
    """创建托盘和隐藏窗口的组合"""
    tray = SystemTray()

    # 创建隐藏的根窗口
    hidden_root = HiddenRoot(tray)

    # 创建主窗口（隐藏根窗口的子窗口）
    main_window = main_window_class(hidden_root)

    # 设置托盘
    tray.setup(hidden_root, on_quit=on_quit)

    return hidden_root, main_window, tray
