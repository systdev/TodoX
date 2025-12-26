"""提醒弹窗组件"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from .styles import COLORS, FONTS, PADDING, SIZES
from .theme import theme


class ReminderPopup(tk.Toplevel):
    """提醒弹窗 - 无关闭按钮"""

    def __init__(self, parent, todo, on_complete=None, on_snooze=None):
        super().__init__(parent)
        self.title("待办提醒")
        self.todo = todo
        self.on_complete = on_complete
        self.on_snooze = on_snooze

        self._setup_window()
        self._build_ui()
        self._center_window()

    def _setup_window(self):
        """设置窗口属性"""
        self.configure(bg=COLORS["card"])
        self.resizable(False, False)
        self.attributes("-topmost", True)  # 置顶
        self.transparency = 0.98  # Windows毛玻璃效果
        self.overrideredirect(True)  # 无标题栏

        # 窗口大小
        self.geometry("380x300")

        # 关闭时不做任何操作（不销毁，只是隐藏）
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        """构建UI"""
        # 主容器
        main_frame = tk.Frame(self, bg=COLORS["card"], bd=2, relief="solid")
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # 标题栏
        header_frame = tk.Frame(main_frame, bg=COLORS["primary"], height=40)
        header_frame.pack(fill="x")
        header_frame.propagate(False)

        # 警告图标
        icon_label = tk.Label(
            header_frame,
            text="⚠",
            font=("Microsoft YaHei", 20),
            bg=COLORS["primary"],
            fg="white"
        )
        icon_label.pack(side="left", padx=PADDING["medium"], pady=5)

        title_label = tk.Label(
            header_frame,
            text="待办提醒",
            font=FONTS["subtitle"],
            bg=COLORS["primary"],
            fg="white"
        )
        title_label.pack(side="left", pady=5)

        # 内容区域
        content_frame = tk.Frame(main_frame, bg=COLORS["card"], pady=PADDING["medium"])
        content_frame.pack(fill="both", expand=True, padx=PADDING["large"])

        # 任务标题
        theme.apply_label_style(title_label := tk.Label(
            content_frame,
            text=self.todo.title,
            font=("Microsoft YaHei", 14, "bold"),
            fg=COLORS["text"],
            bg=COLORS["card"],
            wraplength=320
        ), "title")
        title_label.pack(anchor="w", pady=(0, PADDING["small"]))

        # 提醒时间
        if self.todo.reminder_time:
            time_str = self.todo.reminder_time.strftime("%Y-%m-%d %H:%M")
        else:
            time_str = "无"
        time_label = tk.Label(
            content_frame,
            text=f"时间: {time_str}",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["card"]
        )
        time_label.pack(anchor="w", pady=(0, PADDING["small"]))

        # 标签
        if self.todo.tags:
            tags_text = " ".join([f"#{t.name}" for t in self.todo.tags])
            tags_label = tk.Label(
                content_frame,
                text=tags_text,
                font=FONTS["small"],
                fg=COLORS["primary"],
                bg=COLORS["card"]
            )
            tags_label.pack(anchor="w")

        # 稍后提醒选项
        snooze_frame = tk.Frame(content_frame, bg=COLORS["card"])
        snooze_frame.pack(fill="x", pady=PADDING["medium"])

        theme.apply_label_style(
            tk.Label(snooze_frame, text="稍后提醒:", bg=COLORS["card"]),
            "small"
        )
        snooze_frame.pack(anchor="w")

        # 稍后提醒按钮
        btn_frame = tk.Frame(content_frame, bg=COLORS["card"])
        btn_frame.pack(fill="x", pady=PADDING["small"])

        for minutes in [2, 5, 10, 15, 30]:
            btn = tk.Button(
                btn_frame,
                text=f"{minutes}分钟",
                font=FONTS["small"],
                bg=COLORS["frame"],
                fg=COLORS["text"],
                relief="flat",
                bd=0,
                padx=PADDING["medium"],
                pady=4,
                command=lambda m=minutes: self._on_snooze(m)
            )
            btn.pack(side="left", padx=(0, PADDING["small"]))

            # 悬停效果
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLORS["border"]))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=COLORS["frame"]))

        # 底部按钮
        btn_bottom_frame = tk.Frame(main_frame, bg=COLORS["card"], height=50, pady=PADDING["medium"])
        btn_bottom_frame.pack(fill="x")
        btn_bottom_frame.propagate(False)

        # 完成按钮
        complete_btn = tk.Button(
            btn_bottom_frame,
            text="✓ 完成",
            font=FONTS["button"],
            bg=COLORS["success"],
            fg="white",
            relief="flat",
            bd=0,
            padx=PADDING["xlarge"],
            pady=PADDING["small"],
            command=self._on_complete
        )
        complete_btn.pack(side="right", padx=PADDING["medium"])

        complete_btn.bind("<Enter>", lambda e: complete_btn.configure(bg="#43A047"))
        complete_btn.bind("<Leave>", lambda e: complete_btn.configure(bg=COLORS["success"]))

    def _center_window(self):
        """窗口居中"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _on_complete(self):
        """完成按钮点击"""
        if self.on_complete:
            self.on_complete(self.todo)
        self.destroy()

    def _on_snooze(self, minutes):
        """稍后提醒"""
        if self.on_snooze:
            self.on_snooze(self.todo, minutes)
        self.destroy()

    def _on_close(self):
        """关闭弹窗 - 隐藏但不销毁"""
        self.withdraw()


class TaskCompletedPopup(tk.Toplevel):
    """任务完成提示弹窗"""

    def __init__(self, parent, task_count=1):
        super().__init__(parent)
        self.title("提示")
        self.task_count = task_count

        self._setup_window()
        self._build_ui()
        self._center_window()

    def _setup_window(self):
        """设置窗口属性"""
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transparency = 0.98
        self.overrideredirect(True)

        self.geometry("280x120")

    def _build_ui(self):
        """构建UI"""
        main_frame = tk.Frame(self, bg=COLORS["card"], bd=2, relief="solid")
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # 内容
        content_frame = tk.Frame(main_frame, bg=COLORS["card"])
        content_frame.pack(fill="both", expand=True, padx=PADDING["large"], pady=PADDING["large"])

        icon_label = tk.Label(
            content_frame,
            text="✓",
            font=("Microsoft YaHei", 32),
            bg=COLORS["card"],
            fg=COLORS["success"]
        )
        icon_label.pack(pady=(0, PADDING["small"]))

        msg = f"已完成任务" if self.task_count == 1 else f"已完成 {self.task_count} 个任务"
        label = tk.Label(
            content_frame,
            text=msg,
            font=FONTS["body"],
            bg=COLORS["card"],
            fg=COLORS["success"]
        )
        label.pack()

        # 自动关闭
        self.after(1500, self.destroy)

    def _center_window(self):
        """窗口居中"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
