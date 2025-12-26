"""待办表单组件"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from .styles import COLORS, FONTS, PADDING
from .theme import theme


class TodoForm(tk.Toplevel):
    """待办表单对话框"""

    def __init__(self, parent, todo=None, readonly=False, on_save=None):
        super().__init__(parent)
        self.title("查看待办" if readonly else ("编辑待办" if todo else "添加待办"))
        self.todo = todo
        self.readonly = readonly
        self.on_save = on_save

        self._result = None
        self._setup_window()
        self._build_ui()
        self._load_data()

        # 如果是只读模式，禁用所有输入
        if self.readonly:
            self._set_readonly()

    def _setup_window(self):
        """设置窗口"""
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.geometry("450x680")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _build_ui(self):
        """构建UI"""
        main_frame = tk.Frame(self, bg=COLORS["background"], padx=PADDING["large"], pady=PADDING["medium"])
        main_frame.pack(fill="both", expand=True)

        # ========== 标题行 ==========
        title_row = tk.Frame(main_frame, bg=COLORS["background"])
        title_row.pack(fill="x", pady=(0, PADDING["small"]))

        tk.Label(title_row, text="标题 *", bg=COLORS["background"], font=FONTS["body"], fg=COLORS["danger"]).pack(anchor="w")
        self.title_entry = tk.Entry(title_row, font=FONTS["body"])
        theme.apply_entry_style(self.title_entry)
        self.title_entry.pack(fill="x", pady=(2, 0))

        # ========== 描述行 ==========
        desc_row = tk.Frame(main_frame, bg=COLORS["background"])
        desc_row.pack(fill="x", pady=(0, PADDING["medium"]))

        tk.Label(desc_row, text="描述", bg=COLORS["background"], font=FONTS["body"]).pack(anchor="w")
        self.desc_text = tk.Text(desc_row, font=FONTS["body"], height=3, wrap="word")
        theme.apply_entry_style(self.desc_text)
        self.desc_text.pack(fill="x", pady=(2, 0))

        # ========== 优先级和分类行 ==========
        row1 = tk.Frame(main_frame, bg=COLORS["background"])
        row1.pack(fill="x", pady=(0, PADDING["medium"]))

        # 优先级
        priority_frame = tk.Frame(row1, bg=COLORS["background"])
        priority_frame.pack(side="left", fill="x", expand=True)

        tk.Label(priority_frame, text="优先级", bg=COLORS["background"], font=FONTS["body"]).pack(anchor="w")
        self.priority_var = tk.StringVar(value="中")
        self.priority_combo = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["高", "中", "低"],
            state="readonly",
            width=10,
            font=FONTS["body"]
        )
        self.priority_combo.pack(anchor="w", pady=(2, 0))
        theme.apply_combobox_style(self.priority_combo)

        # 分类
        category_frame = tk.Frame(row1, bg=COLORS["background"])
        category_frame.pack(side="left", fill="x", expand=True, padx=PADDING["medium"])

        tk.Label(category_frame, text="分类", bg=COLORS["background"], font=FONTS["body"]).pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            state="readonly",
            width=15,
            font=FONTS["body"]
        )
        self.category_combo.pack(anchor="w", pady=(2, 0))

        # 标签选择
        tag_row = tk.Frame(main_frame, bg=COLORS["background"])
        tag_row.pack(fill="x", pady=(0, PADDING["medium"]))

        tk.Label(tag_row, text="标签", bg=COLORS["background"], font=FONTS["body"]).pack(anchor="w")
        self.tag_frame = tk.Frame(tag_row, bg=COLORS["background"])
        self.tag_frame.pack(fill="x", pady=(2, 0))
        self.tag_vars = {}

        # 分隔线
        sep1 = ttk.Separator(main_frame, orient="horizontal")
        sep1.pack(fill="x", pady=PADDING["small"])

        # ========== 提醒设置 ==========
        theme.apply_label_style(
            tk.Label(main_frame, text="提醒时间", bg=COLORS["background"]),
            "subtitle"
        )
        sep1.pack(fill="x", pady=PADDING["tiny"])

        # 无需提醒选项（显示在日期上方，默认勾选）
        self.no_reminder_var = tk.BooleanVar(value=True)
        self.no_reminder_cb = tk.Checkbutton(
            main_frame,
            text="无需提醒",
            variable=self.no_reminder_var,
            command=self._on_no_reminder_toggle,
            font=FONTS["body"],
            bg=COLORS["background"],
            selectcolor=COLORS["background"]
        )
        theme.apply_checkbox_style(self.no_reminder_cb)
        self.no_reminder_cb.pack(anchor="w", pady=(0, PADDING["small"]))

        # 日期时间选择
        self.datetime_frame = tk.Frame(main_frame, bg=COLORS["background"])
        self.datetime_frame.pack(fill="x", pady=(0, PADDING["medium"]))

        # 日期选择行
        date_row = tk.Frame(self.datetime_frame, bg=COLORS["background"])
        date_row.pack(fill="x", pady=(0, PADDING["small"]))

        tk.Label(date_row, text="日期", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 年份选择
        current_year = datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(
            date_row,
            textvariable=self.year_var,
            values=[str(y) for y in range(current_year - 1, current_year + 6)],
            width=6,
            font=FONTS["body"],
            state="readonly"
        )
        year_combo.pack(side="left", padx=(5, 0))
        year_combo.bind("<<ComboboxSelected>>", self._update_day_combo)

        tk.Label(date_row, text="年", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 月份选择
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        month_combo = ttk.Combobox(
            date_row,
            textvariable=self.month_var,
            values=[str(m) for m in range(1, 13)],
            width=4,
            font=FONTS["body"],
            state="readonly"
        )
        month_combo.pack(side="left", padx=(PADDING["small"], 0))
        month_combo.bind("<<ComboboxSelected>>", self._update_day_combo)

        tk.Label(date_row, text="月", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 日期选择
        self.day_var = tk.StringVar(value=str(datetime.now().day))
        self.day_combo = ttk.Combobox(
            date_row,
            textvariable=self.day_var,
            values=[str(d) for d in range(1, 32)],
            width=4,
            font=FONTS["body"],
            state="readonly"
        )
        self.day_combo.pack(side="left", padx=(PADDING["small"], 0))

        tk.Label(date_row, text="日", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 时间选择行
        time_row = tk.Frame(self.datetime_frame, bg=COLORS["background"])
        time_row.pack(fill="x")

        tk.Label(time_row, text="时间", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 小时选择
        self.hour_var = tk.StringVar(value=str(datetime.now().hour))
        hour_combo = ttk.Combobox(
            time_row,
            textvariable=self.hour_var,
            values=[f"{h:02d}" for h in range(24)],
            width=4,
            font=FONTS["body"],
            state="readonly"
        )
        hour_combo.pack(side="left", padx=(5, 0))

        tk.Label(time_row, text="时", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 分钟选择
        self.minute_var = tk.StringVar(value="00")
        minute_combo = ttk.Combobox(
            time_row,
            textvariable=self.minute_var,
            values=[f"{m:02d}" for m in range(60)],
            width=4,
            font=FONTS["body"],
            state="readonly"
        )
        minute_combo.pack(side="left", padx=(PADDING["small"], 0))

        tk.Label(time_row, text="分", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 分隔线
        sep2 = ttk.Separator(main_frame, orient="horizontal")
        sep2.pack(fill="x", pady=PADDING["small"])

        # ========== 循环提醒 ==========
        theme.apply_label_style(
            tk.Label(main_frame, text="循环提醒", bg=COLORS["background"]),
            "subtitle"
        )
        sep2.pack(fill="x", pady=PADDING["tiny"])

        # 启用循环
        self.recurring_var = tk.BooleanVar(value=False)
        self.recurring_cb = tk.Checkbutton(
            main_frame,
            text="启用循环提醒",
            variable=self.recurring_var,
            command=self._on_recurring_toggle,
            font=FONTS["body"],
            bg=COLORS["background"],
            selectcolor=COLORS["background"]
        )
        theme.apply_checkbox_style(self.recurring_cb)
        self.recurring_cb.pack(anchor="w", pady=(0, PADDING["small"]))

        # 循环设置
        self.recurring_frame = tk.Frame(main_frame, bg=COLORS["background"])
        self.recurring_frame.pack(fill="x", pady=(0, PADDING["small"]))

        # 循环类型
        type_row = tk.Frame(self.recurring_frame, bg=COLORS["background"])
        type_row.pack(fill="x", pady=(0, PADDING["small"]))

        tk.Label(type_row, text="类型", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")
        self.recurring_type_var = tk.StringVar(value="每天")
        self.recurring_type_combo = ttk.Combobox(
            type_row,
            textvariable=self.recurring_type_var,
            values=["每天", "每周"],
            state="readonly",
            width=10,
            font=FONTS["body"]
        )
        self.recurring_type_combo.pack(side="left", padx=(5, 0))
        self.recurring_type_combo.bind("<<ComboboxSelected>>", self._on_recurring_type_change)

        # 周几选择（仅每周显示）
        self.weekday_frame = tk.Frame(self.recurring_frame, bg=COLORS["background"])
        self.weekday_frame.pack(fill="x", pady=(PADDING["small"], 0))
        self.weekday_vars = {}
        self.weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i, day in enumerate(self.weekday_names):
            var = tk.BooleanVar(value=False)
            self.weekday_vars[i] = var
            cb = tk.Checkbutton(
                self.weekday_frame,
                text=day,
                variable=var,
                font=FONTS["body"],
                bg=COLORS["background"],
                selectcolor=COLORS["background"]
            )
            theme.apply_checkbox_style(cb)
            cb.pack(side="left", padx=(0, PADDING["small"]))

        # 循环时间
        time_row2 = tk.Frame(self.recurring_frame, bg=COLORS["background"])
        time_row2.pack(fill="x", pady=(PADDING["small"], 0))

        tk.Label(time_row2, text="时间", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 循环小时
        self.recurring_hour_var = tk.StringVar(value="08")
        recurring_hour_combo = ttk.Combobox(
            time_row2,
            textvariable=self.recurring_hour_var,
            values=[f"{h:02d}" for h in range(24)],
            width=4,
            font=FONTS["body"],
            state="readonly"
        )
        recurring_hour_combo.pack(side="left", padx=(5, 0))
        tk.Label(time_row2, text="时", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 循环分钟
        self.recurring_minute_var = tk.StringVar(value="00")
        recurring_minute_combo = ttk.Combobox(
            time_row2,
            textvariable=self.recurring_minute_var,
            values=[f"{m:02d}" for m in range(60)],
            width=4,
            font=FONTS["body"],
            state="readonly"
        )
        recurring_minute_combo.pack(side="left", padx=(PADDING["small"], 0))
        tk.Label(time_row2, text="分", bg=COLORS["background"], font=FONTS["body"]).pack(side="left")

        # 排除假期（仅"每天"时显示）
        self.exclude_holidays_var = tk.BooleanVar(value=False)
        self.exclude_holidays_cb = tk.Checkbutton(
            self.recurring_frame,
            text="排除假期",
            variable=self.exclude_holidays_var,
            font=FONTS["body"],
            bg=COLORS["background"],
            selectcolor=COLORS["background"]
        )
        theme.apply_checkbox_style(self.exclude_holidays_cb)
        self.exclude_holidays_cb.pack(anchor="w", pady=(0, PADDING["medium"]))

        # ========== 按钮 ==========
        btn_frame = tk.Frame(main_frame, bg=COLORS["background"])
        btn_frame.pack(fill="x", pady=PADDING["medium"])

        cancel_btn = tk.Button(
            btn_frame,
            text="取消",
            font=FONTS["button"],
            bg=COLORS["frame"],
            fg=COLORS["text"],
            relief="flat",
            bd=0,
            padx=PADDING["xlarge"],
            pady=PADDING["small"],
            command=self._on_cancel
        )
        cancel_btn.pack(side="right", padx=(PADDING["medium"], 0))
        self._cancel_btn = cancel_btn

        save_btn = tk.Button(
            btn_frame,
            text="保存",
            font=FONTS["button"],
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            bd=0,
            padx=PADDING["xlarge"],
            pady=PADDING["small"],
            command=self._on_save
        )
        save_btn.pack(side="right")
        self.save_btn = save_btn

        # 初始状态
        self._on_no_reminder_toggle()
        self._on_recurring_toggle()

    def _set_readonly(self):
        """设置只读模式 - 禁用所有输入控件"""
        # 隐藏保存按钮
        if hasattr(self, 'save_btn'):
            self.save_btn.pack_forget()

        # 将取消按钮改为关闭
        if hasattr(self, '_cancel_btn'):
            self._cancel_btn.configure(text="关闭", bg=COLORS["frame"])
            self._cancel_btn.bind("<Enter>", lambda e: self._cancel_btn.configure(bg=COLORS["border"]))
            self._cancel_btn.bind("<Leave>", lambda e: self._cancel_btn.configure(bg=COLORS["frame"]))

        # 禁用所有输入控件（除了取消按钮）
        main_frame = self.winfo_children()[0] if self.winfo_children() else None
        if main_frame:
            for child in main_frame.winfo_children():
                if child != self._cancel_btn.master:  # 排除按钮所在的frame
                    self._disable_widget_except(child, self._cancel_btn)

    def _disable_widget_except(self, widget, except_widget):
        """递归禁用控件，除了指定控件"""
        if widget == except_widget:
            return
        try:
            if hasattr(widget, 'configure') and widget != except_widget:
                widget.configure(state="disabled")
        except tk.TclError:
            pass
        # 递归处理子控件
        for child in widget.winfo_children():
            self._disable_widget_except(child, except_widget)

    def _disable_widget(self, widget):
        """递归禁用控件"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(state="disabled")
        except tk.TclError:
            pass
        # 递归处理子控件
        for child in widget.winfo_children():
            self._disable_widget(child)

    def _on_no_reminder_toggle(self):
        """无需提醒切换"""
        state = "normal" if not self.no_reminder_var.get() else "disabled"
        # 禁用/启用所有子元素（包括嵌套的）
        for child in self.datetime_frame.winfo_children():
            self._set_widget_state(child, state)

    def _update_day_combo(self, event=None):
        """根据选择的年份和月份更新日期下拉菜单"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
        except (ValueError, TypeError):
            return

        # 根据月份确定天数
        if month in [1, 3, 5, 7, 8, 10, 12]:
            days = 31
        elif month in [4, 6, 9, 11]:
            days = 30
        else:  # 2月
            # 判断闰年
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days = 29
            else:
                days = 28

        # 更新日期下拉菜单
        day_values = [str(d) for d in range(1, days + 1)]
        self.day_combo['values'] = day_values

        # 确保当前选择的天数有效
        current_day = int(self.day_var.get())
        if current_day > days:
            self.day_var.set(str(days))
        elif current_day < 1:
            self.day_var.set("1")

    def _on_recurring_toggle(self):
        """循环提醒切换"""
        state = "normal" if self.recurring_var.get() else "disabled"
        # 禁用/启用所有子元素（包括嵌套的）
        for child in self.recurring_frame.winfo_children():
            self._set_widget_state(child, state)
        self._on_recurring_type_change()

    def _set_widget_state(self, widget, state):
        """递归设置控件状态"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(state=state)
        except tk.TclError:
            pass
        # 递归处理子控件
        for child in widget.winfo_children():
            self._set_widget_state(child, state)

    def _on_recurring_type_change(self, event=None):
        """循环类型切换 - 显示/隐藏周几选择和排除假期"""
        # 只在启用状态下才显示/隐藏
        if self.recurring_var.get():
            if self.recurring_type_var.get() == "每周":
                self.weekday_frame.pack(fill="x", pady=(PADDING["small"], 0))
                # 每周不显示排除假期
                self.exclude_holidays_cb.pack_forget()
            else:
                self.weekday_frame.pack_forget()
                # 每天显示排除假期
                self.exclude_holidays_cb.pack(anchor="w", pady=(0, PADDING["medium"]))
        else:
            self.weekday_frame.pack_forget()
            self.exclude_holidays_cb.pack_forget()

    def _load_data(self):
        """加载数据"""
        if self.todo:
            # 标题
            self.title_entry.insert(0, self.todo.title)

            # 描述
            self.desc_text.insert("1.0", self.todo.description)

            # 优先级
            priority_map = {"高": 1, "中": 2, "低": 3}
            priority_text = {v: k for k, v in priority_map.items()}.get(self.todo.priority, "中")
            self.priority_var.set(priority_text)

            # 分类
            if self.todo.category:
                self.category_var.set(self.todo.category.name)

            # 标签
            for tag_id, var in self.tag_vars.items():
                var.set(False)
            for tag in self.todo.tags:
                if tag.id in self.tag_vars:
                    self.tag_vars[tag.id].set(True)

            # 提醒时间
            if self.todo.reminder_time:
                self.no_reminder_var.set(False)
                dt = self.todo.reminder_time
                self.year_var.set(str(dt.year))
                self.month_var.set(str(dt.month))
                self.day_var.set(str(dt.day))
                self.hour_var.set(f"{dt.hour:02d}")
                self.minute_var.set(f"{dt.minute:02d}")
            else:
                self.no_reminder_var.set(True)

            # 循环提醒
            self.recurring_var.set(self.todo.is_recurring)
            if self.todo.is_recurring:
                type_map = {"daily": "每天", "weekly": "每周"}
                self.recurring_type_var.set(type_map.get(self.todo.recurring_type, "每天"))
                if self.todo.recurring_time:
                    self.recurring_hour_var.set(f"{self.todo.recurring_time.hour:02d}")
                    self.recurring_minute_var.set(f"{self.todo.recurring_time.minute:02d}")
                # 加载周几选择
                weekdays = self.todo.get_recurring_weekdays()
                for day_idx in weekdays:
                    if day_idx in self.weekday_vars:
                        self.weekday_vars[day_idx].set(True)
            self.exclude_holidays_var.set(self.todo.exclude_holidays)

    def set_categories(self, categories):
        """设置分类列表"""
        self.category_combo['values'] = [c.name for c in categories]
        if categories:
            self.category_var.set(categories[0].name)

    def set_tags(self, tags):
        """设置标签列表"""
        for widget in self.tag_frame.winfo_children():
            widget.destroy()
        self.tag_vars.clear()

        for tag in tags:
            var = tk.BooleanVar(value=False)
            self.tag_vars[tag.id] = var

            cb = tk.Checkbutton(
                self.tag_frame,
                text=tag.name,
                variable=var,
                font=FONTS["body"],
                bg=COLORS["background"],
                selectcolor=COLORS["background"]
            )
            theme.apply_checkbox_style(cb)
            cb.pack(side="left", padx=(0, PADDING["medium"]))

            # 只读模式下禁用标签checkbox
            if self.readonly:
                cb.configure(state="disabled")

    def _on_cancel(self):
        """取消"""
        self._result = None
        self.destroy()

    def _on_save(self):
        """保存"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("提示", "请输入标题")
            return

        # 获取分类ID
        category_name = self.category_var.get()
        from ..database import db
        categories = db.get_all_categories()
        category_id = None
        for c in categories:
            if c.name == category_name:
                category_id = c.id
                break

        # 获取标签ID
        tag_ids = [tid for tid, var in self.tag_vars.items() if var.get()]

        # 提醒时间
        reminder_time = None
        if not self.no_reminder_var.get():
            try:
                year = int(self.year_var.get())
                month = int(self.month_var.get())
                day = int(self.day_var.get())
                hour = int(self.hour_var.get())
                minute = int(self.minute_var.get())
                reminder_time = datetime(year, month, day, hour, minute)
            except (ValueError, TypeError):
                messagebox.showwarning("提示", "请选择有效的日期和时间")
                return

        # 循环提醒
        is_recurring = self.recurring_var.get()
        recurring_type_map = {"每天": "daily", "每周": "weekly"}
        recurring_type = None
        recurring_time = None
        recurring_weekdays = None
        if is_recurring:
            recurring_type = recurring_type_map.get(self.recurring_type_var.get())
            try:
                hour = int(self.recurring_hour_var.get())
                minute = int(self.recurring_minute_var.get())
                from datetime import time as dt_time
                recurring_time = dt_time(hour, minute)
            except (ValueError, TypeError):
                pass
            # 获取选中的周几
            if self.recurring_type_var.get() == "每周":
                recurring_weekdays = [day for day, var in self.weekday_vars.items() if var.get()]

        data = {
            "title": title,
            "description": self.desc_text.get("1.0", "end").strip(),
            "priority": {"高": 1, "中": 2, "低": 3}.get(self.priority_var.get(), 2),
            "category_id": category_id,
            "tag_ids": tag_ids,
            "reminder_time": reminder_time,
            "is_recurring": is_recurring,
            "recurring_type": recurring_type,
            "recurring_time": recurring_time,
            "recurring_weekdays": recurring_weekdays,
            "exclude_holidays": self.exclude_holidays_var.get()
        }

        self._result = data
        if self.on_save:
            self.on_save(data)
        self.destroy()

    def get_result(self):
        """获取结果"""
        return self._result
