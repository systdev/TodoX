"""主窗口"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from .styles import COLORS, FONTS, PADDING, SIZES
from .theme import theme
from .todo_list import TodoList
from .todo_form import TodoForm
from .notification import ReminderPopup, TaskCompletedPopup
from ..database import db
from ..models import Todo, Tag


class MainWindow(tk.Frame):
    """主窗口"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self._current_filter = "all"  # all, pending, completed
        self._search_keyword = ""
        self._current_category = None
        self._current_tag = None

        self._build_ui()

    def _build_ui(self):
        """构建UI"""
        # 配置主框架背景
        self.configure(bg=COLORS["background"])

        # ========== 顶部工具栏 ==========
        toolbar = tk.Frame(self, bg=COLORS["card"], height=50)
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)

        # 搜索框
        search_frame = tk.Frame(toolbar, bg=COLORS["card"])
        search_frame.pack(side="left", padx=PADDING["medium"], pady=PADDING["small"])

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=20,
            font=FONTS["body"],
            fg=COLORS["text_secondary"]
        )
        theme.apply_entry_style(search_entry)
        search_entry.pack(side="left")
        search_entry.insert(0, "搜索...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end") if search_entry.get() == "搜索..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "搜索...") if not search_entry.get() else None)

        # 分类筛选
        self.category_var = tk.StringVar(value="全部分类")
        self.category_combo = ttk.Combobox(
            toolbar,
            textvariable=self.category_var,
            state="readonly",
            width=12,
            font=FONTS["body"]
        )
        self.category_combo.pack(side="left", padx=PADDING["small"])
        self.category_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # 标签筛选
        self.tag_var = tk.StringVar(value="全部标签")
        self.tag_combo = ttk.Combobox(
            toolbar,
            textvariable=self.tag_var,
            state="readonly",
            width=12,
            font=FONTS["body"]
        )
        self.tag_combo.pack(side="left", padx=PADDING["small"])
        self.tag_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # 添加按钮
        add_btn = tk.Button(
            toolbar,
            text="+ 添加",
            font=FONTS["button"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            bd=0,
            padx=PADDING["medium"],
            pady=PADDING["small"],
            command=self._on_add_todo
        )
        add_btn.pack(side="right", padx=(0, PADDING["small"]), pady=PADDING["small"])
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=COLORS["primary_dark"]))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=COLORS["primary"]))

        # 标签管理按钮移到状态栏右侧

        # ========== 任务列表 ==========
        list_container = tk.Frame(self, bg=COLORS["background"], padx=PADDING["medium"], pady=PADDING["medium"])
        list_container.pack(fill="both", expand=True)

        self.todo_list = TodoList(
            list_container,
            on_item_click=self._on_edit_todo,
            on_item_right_click=self._on_batch_action
        )
        self.todo_list.pack(fill="both", expand=True)

        # ========== 底部状态栏 ==========
        status_bar = tk.Frame(self, bg=COLORS["card"], height=40)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        # 状态标签
        self.status_label = tk.Label(
            status_bar,
            text="",
            font=FONTS["small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["card"]
        )
        self.status_label.pack(side="left", padx=PADDING["medium"], pady=PADDING["small"])

        # 统计信息
        stats_label = tk.Label(
            status_bar,
            text="",
            font=FONTS["small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["card"]
        )
        stats_label.pack(side="right", padx=PADDING["medium"], pady=PADDING["small"])

        # 关于标签
        about_label = tk.Label(
            status_bar,
            text="关于",
            font=FONTS["small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["card"],
            cursor="hand2"
        )
        about_label.pack(side="right", padx=PADDING["medium"], pady=PADDING["small"])
        about_label.bind("<Button-1>", self._show_about_menu)
        about_label.bind("<Enter>", lambda e: about_label.configure(fg=COLORS["primary"]))
        about_label.bind("<Leave>", lambda e: about_label.configure(fg=COLORS["text_secondary"]))

        # 筛选按钮
        filter_frame = tk.Frame(status_bar, bg=COLORS["card"])
        filter_frame.pack(side="left", padx=PADDING["medium"])

        for text, value in [("全部", "all"), ("待完成", "pending"), ("已完成", "completed")]:
            btn = tk.Button(
                filter_frame,
                text=text,
                font=FONTS["small"],
                bg=COLORS["frame"],
                fg=COLORS["text"],
                relief="flat",
                bd=0,
                padx=PADDING["medium"],
                pady=4,
                command=lambda v=value: self._set_filter(v)
            )
            btn.pack(side="left", padx=(0, PADDING["small"]))
            if value == "all":
                self._filter_buttons = {"all": btn}
            else:
                self._filter_buttons[value] = btn

        self._update_filter_buttons()

        # 右侧按钮区域
        right_frame = tk.Frame(status_bar, bg=COLORS["card"])
        right_frame.pack(side="right", padx=PADDING["medium"])

        # 刷新按钮
        refresh_btn = tk.Button(
            right_frame,
            text="刷新",
            font=FONTS["small"],
            bg=COLORS["frame"],
            fg=COLORS["text"],
            relief="flat",
            bd=0,
            padx=PADDING["medium"],
            pady=4,
            command=self._refresh_data
        )
        refresh_btn.pack(side="right", padx=(0, PADDING["medium"]))
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.configure(bg=COLORS["border"]))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.configure(bg=COLORS["frame"]))

        # 标签管理按钮
        tag_btn = tk.Button(
            right_frame,
            text="标签管理",
            font=FONTS["small"],
            bg=COLORS["frame"],
            fg=COLORS["text"],
            relief="flat",
            bd=0,
            padx=PADDING["medium"],
            pady=4,
            command=self._on_manage_tags
        )
        tag_btn.pack(side="right", padx=(0, PADDING["medium"]))
        tag_btn.bind("<Enter>", lambda e: tag_btn.configure(bg=COLORS["border"]))
        tag_btn.bind("<Leave>", lambda e: tag_btn.configure(bg=COLORS["frame"]))

        # 加载初始数据
        self._refresh_data()

    def _refresh_data(self):
        """刷新数据"""
        # 加载分类
        categories = db.get_all_categories()
        self.category_combo['values'] = ["全部分类"] + [c.name for c in categories]

        # 加载标签
        tags = db.get_all_tags()
        self.tag_combo['values'] = ["全部标签"] + [t.name for t in tags]

        # 加载待办
        self._load_todos()

        # 更新统计
        self._update_stats()

    def _load_todos(self):
        """加载待办列表"""
        todos = db.search_todos(
            keyword=self._search_keyword,
            category_id=self._current_category,
            tag_id=self._current_tag,
            include_completed=(self._current_filter != "pending")
        )

        # 按状态筛选
        if self._current_filter == "pending":
            todos = [t for t in todos if not t.completed]
        elif self._current_filter == "completed":
            todos = [t for t in todos if t.completed]

        self.todo_list.load_todos(todos)

        # 更新状态栏 - 显示当前筛选后的数量
        todos = db.search_todos(
            keyword=self._search_keyword,
            category_id=self._current_category,
            tag_id=self._current_tag,
            include_completed=(self._current_filter != "pending")
        )
        # 按状态筛选
        if self._current_filter == "pending":
            todos = [t for t in todos if not t.completed]
        elif self._current_filter == "completed":
            todos = [t for t in todos if t.completed]
        self.status_label.config(text=f"共 {len(todos)} 个待办")

    def _update_stats(self):
        """更新统计信息"""
        stats = db.get_stats()
        # 可以在这里更新更多统计信息

    def _update_filter_buttons(self):
        """更新筛选按钮状态"""
        for value, btn in self._filter_buttons.items():
            if value == self._current_filter:
                btn.configure(bg=COLORS["primary"], fg="white")
            else:
                btn.configure(bg=COLORS["frame"], fg=COLORS["text"])

    def _set_filter(self, filter_type):
        """设置筛选"""
        self._current_filter = filter_type
        self._update_filter_buttons()
        self._load_todos()

    def _on_search(self, *args):
        """搜索"""
        # 确保UI已初始化
        if not hasattr(self, 'todo_list'):
            return

        keyword = self.search_var.get()
        if keyword and keyword != "搜索...":
            self._search_keyword = keyword
        else:
            self._search_keyword = ""
        self._load_todos()

    def _on_filter_change(self, event):
        """筛选条件变化"""
        # 确保UI已初始化
        if not hasattr(self, 'todo_list'):
            return

        # 分类
        category_name = self.category_var.get()
        if category_name == "全部分类":
            self._current_category = None
        else:
            categories = db.get_all_categories()
            for c in categories:
                if c.name == category_name:
                    self._current_category = c.id
                    break

        # 标签
        tag_name = self.tag_var.get()
        if tag_name == "全部标签":
            self._current_tag = None
        else:
            tags = db.get_all_tags()
            for t in tags:
                if t.name == tag_name:
                    self._current_tag = t.id
                    break

        self._load_todos()

    def _on_add_todo(self):
        """添加待办"""
        form = TodoForm(
            self,
            on_save=self._save_todo
        )
        form.set_categories(db.get_all_categories())
        form.set_tags(db.get_all_tags())

        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() - form.winfo_width()) // 2
        y = (self.winfo_screenheight() - form.winfo_height()) // 2
        form.geometry(f"+{x}+{y}")

        self.wait_window(form)

    def _on_manage_tags(self):
        """标签管理"""
        from .tag_dialog import TagManageDialog

        dialog = TagManageDialog(
            self,
            on_save=self._on_tag_saved
        )

        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (self.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        self.wait_window(dialog)

    def _on_tag_saved(self):
        """标签保存后的回调"""
        self._refresh_data()

    def _on_edit_todo(self, todo_id):
        """编辑待办"""
        todo = db.get_todo(todo_id)
        if not todo:
            return

        # 已完成状态只能查看，不能编辑
        readonly = todo.completed

        form = TodoForm(
            self,
            todo=todo,
            readonly=readonly,
            on_save=lambda data: self._update_todo(todo_id, data)
        )
        form.set_categories(db.get_all_categories())
        form.set_tags(db.get_all_tags())

        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() - form.winfo_width()) // 2
        y = (self.winfo_screenheight() - form.winfo_height()) // 2
        form.geometry(f"+{x}+{y}")

        self.wait_window(form)

    def _on_batch_action(self, action, todo_ids):
        """批量操作"""
        if action == "complete":
            db.batch_complete(todo_ids)
            TaskCompletedPopup(self, len(todo_ids))
        elif action == "delete":
            if tk.messagebox.askyesno("确认", f"确定删除选中的 {len(todo_ids)} 个任务吗？"):
                db.batch_delete(todo_ids)

        self._refresh_data()

    def _save_todo(self, data):
        """保存新待办"""
        db.create_todo(**data)
        self._refresh_data()

    def _update_todo(self, todo_id, data):
        """更新待办"""
        # 提取tag_ids和recurring_weekdays用于特殊处理
        tag_ids = data.pop("tag_ids", None)
        recurring_weekdays = data.pop("recurring_weekdays", None)

        db.update_todo(todo_id, **data)

        # 更新标签关联
        if tag_ids is not None:
            session = db.session
            todo = session.query(Todo).get(todo_id)
            if todo:
                tags = session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
                todo.tags = tags
                session.commit()
            session.close()

        # 更新循环周几
        if recurring_weekdays is not None:
            session = db.session
            todo = session.query(Todo).get(todo_id)
            if todo:
                todo.set_recurring_weekdays(recurring_weekdays)
                session.commit()
            session.close()

        self._refresh_data()

    def show_reminder(self, todo):
        """显示提醒弹窗"""
        ReminderPopup(
            self,
            todo,
            on_complete=self._on_reminder_complete,
            on_snooze=self._on_reminder_snooze
        )

    def _on_reminder_complete(self, todo):
        """提醒弹窗 - 完成"""
        db.complete_todo(todo.id)
        self._refresh_data()

    def _on_reminder_snooze(self, todo, minutes):
        """提醒弹窗 - 稍后提醒"""
        db.snooze_reminder(todo.id, minutes)
        self._refresh_data()

    def _show_about_menu(self, event=None):
        """显示关于菜单"""
        # 创建弹出菜单
        menu = tk.Menu(self, tearoff=0, bg=COLORS["card"], fg=COLORS["text"])

        menu.add_command(
            label="使用帮助",
            command=self._show_help,
            font=FONTS["body"]
        )
        menu.add_separator()
        menu.add_command(
            label=f"版本: v1.0.0",
            command=self._show_version,
            font=FONTS["body"]
        )

        # 在关于标签位置显示菜单
        x = self.winfo_rootx() + self.winfo_width() - 100
        y = self.winfo_rooty() + self.winfo_height() - 40
        menu.post(x, y)

    def _show_help(self):
        """显示帮助信息"""
        from tkinter import messagebox
        help_text = """TodoX 使用帮助

1. 添加待办
   - 点击"添加"按钮创建新的待办事项

2. 编辑待办
   - 双击列表中的待办进行编辑

3. 完成/删除
   - 右键点击待办可批量完成或删除
   - 支持多选（Ctrl/Shift）

4. 筛选查看
   - 使用顶部的分类和标签筛选
   - 使用底部的状态筛选（全部/待完成/已完成）

5. 提醒设置
   - 添加待办时可设置提醒时间
   - 支持循环提醒（每天/每周）

6. 系统托盘
   - 点击关闭按钮最小化到托盘
   - 双击托盘图标显示窗口"""
        messagebox.showinfo("使用帮助", help_text)

    def _show_version(self):
        """显示版本信息"""
        from tkinter import messagebox
        messagebox.showinfo("关于 TodoX", "TodoX v1.0.0\n\n一个简洁的待办事项管理工具")
