"""TodoX - 待办事项提醒工具"""
import sys
import tkinter as tk
from tkinter import messagebox
import ctypes

from app.ui.main_window import MainWindow
from app.ui.tray_icon import SystemTray
from app.ui.styles import COLORS
from app.reminder import reminder_service
from app.database import db

# 单实例检查
INSTANCE_MUTEX_NAME = "TodoX_SingleInstance_Mutex"


def check_single_instance():
    """检查是否已有实例运行"""
    try:
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, INSTANCE_MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            return False  # 已存在实例
        return True  # 可以启动
    except:
        return True  # 出错时允许启动


class TodoXApp:
    """TodoX应用"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TodoX - 待办事项管理")
        self.root.geometry("1100x600")
        self.root.minsize(600, 400)

        # 设置样式
        self._setup_styles()

        # 创建主窗口
        self.main_window = MainWindow(self.root)
        self.main_window.pack(fill="both", expand=True)

        # 设置提醒服务
        reminder_service.setup(self.main_window)

        # 初始化系统托盘
        self.tray = SystemTray()
        self.tray.setup(self.root, on_quit=self._on_quit)

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 启动提醒服务
        reminder_service.start()

    def _setup_styles(self):
        """设置全局样式"""
        self.root.configure(bg=COLORS["background"])

    def _on_close(self):
        """窗口关闭事件 - 最小化到托盘"""
        self.root.withdraw()
        if not self.tray._running:
            self.tray.run()

    def _on_quit(self):
        """退出程序"""
        reminder_service.stop()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主入口"""
    # 单实例检查
    if not check_single_instance():
        messagebox.showwarning("提示", "TodoX 已在运行中")
        return

    try:
        app = TodoXApp()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败:\n{str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
