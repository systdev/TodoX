"""主题管理"""
import tkinter as tk
from tkinter import ttk

from .styles import COLORS, FONTS, PADDING, SIZES, BORDER_RADIUS


class ThemeManager:
    """主题管理器"""

    _instance = None
    _current_theme = "light"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

    @property
    def current_theme(self):
        return self._current_theme

    def apply_button_style(self, button, style_type="primary"):
        """应用按钮样式"""
        if style_type == "primary":
            button.configure(
                bg=COLORS["primary"],
                fg="white",
                activebackground=COLORS["primary_dark"],
                activeforeground="white",
                font=FONTS["button"],
                relief="flat",
                bd=0,
                padx=PADDING["medium"],
                pady=PADDING["small"]
            )
        elif style_type == "success":
            button.configure(
                bg=COLORS["success"],
                fg="white",
                activebackground=COLORS["success"],
                activeforeground="white",
                font=FONTS["button"],
                relief="flat",
                bd=0,
                padx=PADDING["medium"],
                pady=PADDING["small"]
            )
        elif style_type == "danger":
            button.configure(
                bg=COLORS["danger"],
                fg="white",
                activebackground=COLORS["danger"],
                activeforeground="white",
                font=FONTS["button"],
                relief="flat",
                bd=0,
                padx=PADDING["medium"],
                pady=PADDING["small"]
            )
        elif style_type == "warning":
            button.configure(
                bg=COLORS["warning"],
                fg="white",
                activebackground=COLORS["warning"],
                activeforeground="white",
                font=FONTS["button"],
                relief="flat",
                bd=0,
                padx=PADDING["medium"],
                pady=PADDING["small"]
            )

        # 绑定悬停效果
        button.bind("<Enter>", lambda e: button.configure(bg=COLORS.get(f"{style_type}_dark", COLORS["primary_dark"])))
        button.bind("<Leave>", lambda e: button.configure(bg=COLORS.get(style_type, COLORS["primary"])))

    def apply_label_style(self, label, style_type="body"):
        """应用标签样式"""
        styles = {
            "title": {"font": FONTS["title"], "fg": COLORS["text"]},
            "subtitle": {"font": FONTS["subtitle"], "fg": COLORS["text"]},
            "header": {"font": FONTS["header"], "fg": COLORS["text"]},
            "body": {"font": FONTS["body"], "fg": COLORS["text"]},
            "small": {"font": FONTS["small"], "fg": COLORS["text_secondary"]},
            "muted": {"font": FONTS["body"], "fg": COLORS["text_light"]},
            "success": {"font": FONTS["body"], "fg": COLORS["success"]},
            "warning": {"font": FONTS["body"], "fg": COLORS["warning"]},
            "danger": {"font": FONTS["body"], "fg": COLORS["danger"]},
        }
        style = styles.get(style_type, styles["body"])
        label.configure(**style)

    def apply_entry_style(self, entry):
        """应用输入框样式"""
        entry.configure(
            font=FONTS["entry"],
            fg=COLORS["text"],
            bg=COLORS["card"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border_focus"]
        )

    def apply_frame_style(self, frame, style_type="card"):
        """应用框架样式"""
        bg_colors = {
            "card": COLORS["card"],
            "frame": COLORS["frame"],
            "background": COLORS["background"],
        }
        bg = bg_colors.get(style_type, COLORS["card"])
        frame.configure(bg=bg)

    def apply_treeview_style(self, treeview):
        """应用Treeview样式"""
        style = ttk.Style()
        style.configure(
            "Treeview",
            font=FONTS["treeview"],
            rowheight=32,
            background=COLORS["card"],
            fieldbackground=COLORS["card"],
            foreground=COLORS["text"]
        )
        style.configure(
            "Treeview.Heading",
            font=FONTS["header"],
            background=COLORS["frame"],
            foreground=COLORS["text"]
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", "white")]
        )

    def create_tag_label(self, parent, text, color=COLORS["tag_default"], text_color=None):
        """创建带背景色的标签"""
        if text_color is None:
            # 根据背景色亮度计算文字颜色
            import colorsys
            hex_color = color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            text_color = "#333333" if luminance > 0.5 else "white"

        frame = tk.Frame(parent, bg=color, padx=PADDING["small"], pady=2)
        label = tk.Label(
            frame,
            text=text,
            bg=color,
            fg=text_color,
            font=FONTS["small"]
        )
        label.pack()
        return frame, label

    def apply_dialog_style(self, dialog):
        """应用对话框样式"""
        dialog.configure(bg=COLORS["background"])

    def apply_checkbox_style(self, checkbox):
        """应用复选框样式"""
        checkbox.configure(
            font=FONTS["body"],
            bg=COLORS["background"],
            activebackground=COLORS["background"],
            selectcolor=COLORS["card"]
        )

    def apply_combobox_style(self, combobox):
        """应用下拉框样式"""
        style = ttk.Style()
        style.configure(
            "TCombobox",
            font=FONTS["body"],
            fieldbackground=COLORS["card"],
            background=COLORS["primary"]
        )
        combobox.configure(style="TCombobox")


# 全局主题管理器
theme = ThemeManager()


def apply_style(widget, style_name, **kwargs):
    """快捷样式应用函数"""
    from .styles import get_priority_color

    if style_name == "button_primary":
        theme.apply_button_style(widget, "primary")
    elif style_name == "button_success":
        theme.apply_button_style(widget, "success")
    elif style_name == "button_danger":
        theme.apply_button_style(widget, "danger")
    elif style_name == "button_warning":
        theme.apply_button_style(widget, "warning")
    elif style_name == "label_title":
        theme.apply_label_style(widget, "title")
    elif style_name == "label_body":
        theme.apply_label_style(widget, "body")
    elif style_name == "label_small":
        theme.apply_label_style(widget, "small")
    elif style_name == "entry":
        theme.apply_entry_style(widget)
    elif style_name == "frame_card":
        theme.apply_frame_style(widget, "card")
    elif style_name == "treeview":
        theme.apply_treeview_style(widget)
