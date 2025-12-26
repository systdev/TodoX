"""任务列表组件"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from .styles import COLORS, FONTS, PADDING, get_priority_color
from .theme import theme


class TodoList(tk.Frame):
    """任务列表组件"""

    def __init__(self, parent, on_item_click=None, on_item_right_click=None):
        super().__init__(parent, bg=COLORS["background"])
        self.on_item_click = on_item_click
        self.on_item_right_click = on_item_right_click
        self._sort_column = "priority"  # 默认排序列
        self._sort_reverse = False  # 默认升序
        self._current_todos = []  # 当前待办列表
        self._build_ui()

    def _build_ui(self):
        """构建UI"""
        # 创建Treeview - 添加完成状态列
        columns = ("id", "completed", "title", "priority", "category", "tags", "reminder", "created")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="extended",
            style="Treeview"
        )

        # 设置列
        self.tree.heading("id", text="", command=lambda: self._sort_by_column("id"))
        self.tree.heading("completed", text="状态", command=lambda: self._sort_by_column("completed"))
        self.tree.heading("title", text="任务")
        self.tree.heading("priority", text="优先级", command=lambda: self._sort_by_column("priority"))
        self.tree.heading("category", text="分类")
        self.tree.heading("tags", text="标签")
        self.tree.heading("reminder", text="提醒时间", command=lambda: self._sort_by_column("reminder"))
        self.tree.heading("created", text="创建时间", command=lambda: self._sort_by_column("created"))

        self.tree.column("id", width=0, minwidth=0, stretch=False)  # 隐藏id列
        self.tree.column("completed", width=50, anchor="center")
        self.tree.column("title", width=280)
        self.tree.column("priority", width=60, anchor="center")
        self.tree.column("category", width=80, anchor="center")
        self.tree.column("tags", width=140)
        self.tree.column("reminder", width=100, anchor="center")
        self.tree.column("created", width=100, anchor="center")

        # 应用Treeview样式
        theme.apply_treeview_style(self.tree)

        # 滚动条
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定事件
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)  # 右键点击
        self.tree.bind("<Control-a>", self._on_select_all)  # Ctrl+A 全选

        # 右键菜单
        self._setup_context_menu()

    def _setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0, bg=COLORS["card"], fg=COLORS["text"])

        self.context_menu.add_command(
            label="✓ 完成任务",
            command=self._on_batch_complete,
            font=FONTS["body"]
        )
        self.context_menu.add_command(
            label="✗ 删除任务",
            command=self._on_batch_delete,
            font=FONTS["body"]
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="全选",
            command=self._on_select_all,
            font=FONTS["body"]
        )

    def _on_double_click(self, event):
        """双击编辑"""
        item = self.tree.identify_row(event.y)
        if item:
            todo_id = self.tree.item(item, "values")[0]
            if self.on_item_click:
                self.on_item_click(todo_id)

    def _on_right_click(self, event):
        """右键点击"""
        # 选中点击的行
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
        self.context_menu.post(event.x_root, event.y_root)

    def _on_batch_complete(self):
        """批量完成"""
        selected = self.tree.selection()
        if selected and self.on_item_right_click:
            todo_ids = [self.tree.item(item, "values")[0] for item in selected]
            self.on_item_right_click("complete", todo_ids)

    def _on_batch_delete(self):
        """批量删除"""
        selected = self.tree.selection()
        if selected and self.on_item_right_click:
            todo_ids = [self.tree.item(item, "values")[0] for item in selected]
            self.on_item_right_click("delete", todo_ids)

    def _on_select_all(self, event=None):
        """全选"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def _sort_by_column(self, column):
        """按列排序"""
        if self._sort_column == column:
            # 反转排序
            self._sort_reverse = not self._sort_reverse
        else:
            # 新列，升序
            self._sort_column = column
            self._sort_reverse = False

        # 重新排序并刷新
        self._sort_todos()
        self._refresh_display()

    def _sort_todos(self):
        """对待办列表排序"""
        if not self._current_todos:
            return

        def get_sort_key(todo):
            if self._sort_column == "id":
                return todo.id
            elif self._sort_column == "completed":
                return todo.completed  # 未完成的在前
            elif self._sort_column == "priority":
                return todo.priority
            elif self._sort_column == "reminder":
                return todo.reminder_time or datetime.min
            elif self._sort_column == "created":
                return todo.created_at or datetime.min
            else:
                return todo.id

        self._current_todos.sort(key=get_sort_key, reverse=self._sort_reverse)

    def _refresh_display(self):
        """刷新显示"""
        # 清空现有内容
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 插入新数据
        for todo in self._current_todos:
            self._insert_todo(todo)

    def load_todos(self, todos):
        """加载待办列表"""
        self._current_todos = list(todos)
        # 按当前排序重新排序
        self._sort_todos()
        # 刷新显示
        self._refresh_display()

    def _insert_todo(self, todo):
        """插入单个待办"""
        # 分类名称
        category_name = todo.category.name if todo.category else ""

        # 标签 - 用逗号分隔，不显示#
        if todo.tags:
            tags_text = ", ".join([t.name for t in todo.tags])
        else:
            tags_text = ""

        # 提醒时间
        reminder_text = ""
        if todo.reminder_time:
            reminder_text = todo.reminder_time.strftime("%m-%d %H:%M")
        else:
            reminder_text = ""

        # 创建时间 - 显示完整时间
        created_text = todo.created_at.strftime("%Y-%m-%d %H:%M") if todo.created_at else ""

        # 完成状态
        completed_text = "✓" if todo.completed else "☐"

        # 根据优先级获取颜色
        priority_color = get_priority_color(todo.priority)

        # 插入行
        item_id = self.tree.insert(
            "",
            "end",
            values=(
                todo.id,
                completed_text,
                todo.title,
                todo.priority_text,
                category_name,
                tags_text,
                reminder_text,
                created_text
            )
        )

        # 设置行样式
        if todo.completed:
            self.tree.item(item_id, tags=("completed",))
        else:
            # 检查是否过期
            if todo.reminder_time and todo.reminder_time < datetime.now():
                self.tree.item(item_id, tags=("overdue",))
            else:
                # 使用优先级颜色给标题着色
                color_tag = f"priority_{todo.priority}"
                self.tree.tag_configure(color_tag, foreground=priority_color)
                self.tree.item(item_id, tags=(color_tag,))

        # 配置标签样式
        self.tree.tag_configure("completed", foreground=COLORS["text_disabled"])
        self.tree.tag_configure("overdue", foreground=COLORS["danger"])

    def get_selected_ids(self):
        """获取选中的待办ID列表"""
        return [self.tree.item(item, "values")[0] for item in self.tree.selection()]

    def select_all(self):
        """全选"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def clear_selection(self):
        """清除选择"""
        self.tree.selection_remove(self.tree.selection())
