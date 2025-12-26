"""标签管理对话框"""
import tkinter as tk
from tkinter import ttk, messagebox

from .styles import COLORS, FONTS, PADDING
from .theme import theme


class TagManageDialog(tk.Toplevel):
    """标签管理对话框"""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("标签管理")
        self.parent = parent
        self.on_save = on_save

        self._setup_window()
        self._build_ui()
        self._load_tags()

    def _setup_window(self):
        """设置窗口"""
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.geometry("350x350")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        """构建UI"""
        main_frame = tk.Frame(self, bg=COLORS["background"], padx=PADDING["large"], pady=PADDING["medium"])
        main_frame.pack(fill="both", expand=True)

        # ========== 添加标签区域 ==========
        row1 = tk.Frame(main_frame, bg=COLORS["background"])
        row1.pack(fill="x", pady=(0, PADDING["medium"]))

        tk.Label(row1, text="标签名称", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 输入框容器（用于控制高度）
        entry_frame = tk.Frame(row1, bg=COLORS["background"])
        entry_frame.pack(side="left", padx=(5, PADDING["small"]), fill="x", expand=True)

        self.tag_name_var = tk.StringVar()
        self.tag_name_entry = tk.Entry(entry_frame, textvariable=self.tag_name_var, font=FONTS["body"])
        theme.apply_entry_style(self.tag_name_entry)
        self.tag_name_entry.pack(fill="both", expand=True)

        # 添加按钮
        add_btn = tk.Button(
            row1,
            text="添加",
            font=FONTS["button"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            bd=0,
            padx=PADDING["medium"],
            pady=4,
            command=self._add_tag
        )
        add_btn.pack(side="left")

        # 悬停效果
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=COLORS["primary_dark"]))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=COLORS["primary"]))

        # 分隔线
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.pack(fill="x", pady=PADDING["small"])

        # 标签列表
        theme.apply_label_style(
            tk.Label(main_frame, text="已有标签", bg=COLORS["background"]),
            "subtitle"
        )

        # 列表容器
        list_frame = tk.Frame(main_frame, bg=COLORS["card"], bd=1, relief="solid")
        list_frame.pack(fill="both", expand=True, pady=PADDING["small"])

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # 标签列表
        self.tag_list = tk.Listbox(
            list_frame,
            font=FONTS["body"],
            bg=COLORS["card"],
            fg=COLORS["text"],
            selectbackground=COLORS["primary"],
            selectforeground="white",
            relief="flat",
            bd=0,
            yscrollcommand=scrollbar.set
        )
        self.tag_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tag_list.yview)

        # 按钮区域
        btn_frame = tk.Frame(main_frame, bg=COLORS["background"])
        btn_frame.pack(fill="x", pady=PADDING["medium"])

        # 删除按钮
        delete_btn = tk.Button(
            btn_frame,
            text="删除选中",
            font=FONTS["button"],
            bg=COLORS["danger"],
            fg="white",
            relief="flat",
            bd=0,
            padx=PADDING["medium"],
            pady=PADDING["small"],
            command=self._delete_tag
        )
        delete_btn.pack(side="right")

        # 悬停效果
        delete_btn.bind("<Enter>", lambda e: delete_btn.configure(bg="#D32F2F"))
        delete_btn.bind("<Leave>", lambda e: delete_btn.configure(bg=COLORS["danger"]))

        # 关闭按钮
        close_btn = tk.Button(
            btn_frame,
            text="关闭",
            font=FONTS["button"],
            bg=COLORS["frame"],
            fg=COLORS["text"],
            relief="flat",
            bd=0,
            padx=PADDING["medium"],
            pady=PADDING["small"],
            command=self._on_close
        )
        close_btn.pack(side="right", padx=PADDING["medium"])

        # 悬停效果
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg=COLORS["border"]))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg=COLORS["frame"]))

    def _load_tags(self):
        """加载标签列表"""
        from ..database import db

        self.tags = db.get_all_tags()
        self.tag_list.delete(0, "end")

        for tag in self.tags:
            self.tag_list.insert("end", tag.name)

    def _add_tag(self):
        """添加标签"""
        from ..database import db

        name = self.tag_name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入标签名称")
            return

        # 检查是否已存在
        for tag in self.tags:
            if tag.name == name:
                messagebox.showwarning("提示", "标签已存在")
                return

        # 创建标签
        db.create_tag(name)

        # 清空输入
        self.tag_name_var.set("")

        # 重新加载
        self._load_tags()

        # 回调
        if self.on_save:
            self.on_save()

    def _delete_tag(self):
        """删除标签"""
        from ..database import db

        selected = self.tag_list.curselection()
        if not selected:
            messagebox.showwarning("提示", "请选择要删除的标签")
            return

        index = selected[0]
        tag = self.tags[index]

        # 临时取消置顶，让确认弹窗在最上层
        self.attributes("-topmost", False)

        if messagebox.askyesno("确认", f"确定删除标签「{tag.name}」吗？\n使用该标签的待办将取消该标签。"):
            db.delete_tag(tag.id)
            self._load_tags()

            if self.on_save:
                self.on_save()

        # 恢复置顶
        self.attributes("-topmost", True)

    def _on_close(self):
        """关闭"""
        self.destroy()
