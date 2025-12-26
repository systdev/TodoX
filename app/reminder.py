"""提醒服务"""
import sys
if 'E:/Python/TodoX' not in sys.path:
    sys.path.insert(0, 'E:/Python/TodoX')

import threading
import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger


class ReminderService:
    """提醒服务"""

    _instance = None
    _scheduler = None
    _running = False
    _check_interval = 1  # 检查间隔（秒），1秒检查一次保证及时性

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._main_window = None

    def setup(self, main_window):
        """设置主窗口引用"""
        self._main_window = main_window

    def start(self):
        """启动提醒服务"""
        if self._running:
            return

        self._running = True
        self._scheduler = BackgroundScheduler()

        # 每秒检查一次提醒（保证及时性）
        self._scheduler.add_job(
            self._check_reminders,
            IntervalTrigger(seconds=self._check_interval),
            id='check_reminders',
            replace_existing=True
        )

        # 每天凌晨1点检查循环提醒
        self._scheduler.add_job(
            self._schedule_recurring,
            CronTrigger(hour=1, minute=0),
            id='schedule_recurring',
            replace_existing=True
        )

        self._scheduler.start()

    def stop(self):
        """停止提醒服务"""
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
        self._running = False

    def _check_reminders(self):
        """检查提醒"""
        if not self._main_window:
            return

        from app.database import db

        try:
            # 获取需要提醒的待办
            todos = db.get_todos_to_remind()

            for todo in todos:
                # 显示提醒弹窗
                self._main_window.show_reminder(todo)

        except Exception as e:
            pass  # 静默处理

    def _schedule_recurring(self):
        """调度循环提醒"""
        if not self._main_window:
            return

        from app.database import db

        try:
            # 获取今天需要循环提醒的待办
            todos = db.get_recurring_todos_for_today()

            for todo in todos:
                self._main_window.show_reminder(todo)

        except Exception as e:
            pass  # 静默处理

    def snooze(self, todo_id, minutes):
        """稍后提醒"""
        from app.database import db
        db.snooze_reminder(todo_id, minutes)


# 全局提醒服务实例
reminder_service = ReminderService()
