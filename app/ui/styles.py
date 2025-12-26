"""样式常量配置"""
import tkinter as tk

# ========== 颜色配置 ==========
COLORS = {
    # 主色调
    "primary": "#4A90D9",       # 蓝色
    "primary_dark": "#357ABD",
    "primary_light": "#6BA5E7",

    # 状态色
    "success": "#4CAF50",       # 绿色
    "warning": "#FF9800",       # 橙色
    "danger": "#F44336",        # 红色
    "info": "#2196F3",          # 浅蓝

    # 优先级颜色
    "priority_high": "#F44336",   # 高 - 红色
    "priority_medium": "#FF9800", # 中 - 橙色
    "priority_low": "#4CAF50",    # 低 - 绿色

    # 背景色
    "background": "#F5F5F5",    # 浅灰背景
    "card": "#FFFFFF",          # 卡片白
    "frame": "#EEEEEE",         # 框架灰

    # 文字色
    "text": "#333333",          # 主文字
    "text_secondary": "#666666",# 次要文字
    "text_light": "#999999",    # 浅色文字
    "text_disabled": "#BBBBBB", # 禁用文字

    # 边框色
    "border": "#DDDDDD",
    "border_focus": "#4A90D9",

    # 标签颜色
    "tag_default": "#E0E0E0",
}

# ========== 字体配置 ==========
FONTS = {
    "title": ("Microsoft YaHei", 16, "bold"),       # 标题
    "subtitle": ("Microsoft YaHei", 12, "bold"),    # 副标题
    "header": ("Microsoft YaHei", 11, "bold"),      # 表头
    "body": ("Microsoft YaHei", 10),                # 正文
    "small": ("Microsoft YaHei", 9),                # 小字
    "button": ("Microsoft YaHei", 10),              # 按钮
    "entry": ("Microsoft YaHei", 10),               # 输入框
    "treeview": ("Microsoft YaHei", 10),            # 列表
}

# ========== 间距配置 ==========
PADDING = {
    "tiny": 2,
    "small": 5,
    "medium": 10,
    "large": 15,
    "xlarge": 20,
    "xxlarge": 30,
}

# ========== 圆角配置 ==========
BORDER_RADIUS = {
    "small": 4,
    "medium": 8,
    "large": 12,
}

# ========== 组件尺寸 ==========
SIZES = {
    "button_height": 32,
    "entry_height": 28,
    "treeview_height": 400,
    "window_min_width": 600,
    "window_min_height": 500,
}


def get_priority_color(priority):
    """获取优先级对应的颜色"""
    colors = {
        1: COLORS["priority_high"],
        2: COLORS["priority_medium"],
        3: COLORS["priority_low"],
    }
    return colors.get(priority, COLORS["text_secondary"])


def hex_to_rgb(hex_color):
    """十六进制颜色转RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_darker_color(hex_color, factor=0.8):
    """获取更暗的颜色"""
    rgb = hex_to_rgb(hex_color)
    darker = tuple(int(c * factor) for c in rgb)
    return f'#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}'
