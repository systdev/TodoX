"""数据库操作层"""
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import and_, or_

from .models import (
    Todo, Category, Tag, TodoTag, Holiday,
    init_database, get_database_path, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW
)


class Database:
    """数据库操作类"""

    _instance = None
    _engine = None
    _Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """初始化数据库连接"""
        self._engine = init_database()
        self._Session = sessionmaker(bind=self._engine)
        self._ensure_defaults()

    def _ensure_defaults(self):
        """确保默认数据存在"""
        session = self._Session()
        try:
            # 默认分类
            if not session.query(Category).first():
                defaults = [
                    Category(name="工作", color="#4A90D9"),
                    Category(name="日常", color="#4CAF50"),
                    Category(name="学习", color="#FF9800"),
                ]
                session.add_all(defaults)

            # 默认标签
            if not session.query(Tag).first():
                tag_defaults = [
                    Tag(name="紧急"),
                    Tag(name="重要"),
                    Tag(name="日常"),
                ]
                session.add_all(tag_defaults)

            session.commit()
        finally:
            session.close()

    @property
    def session(self):
        """获取新的数据库会话"""
        return self._Session()

    # ========== Todo 操作 ==========

    def get_all_todos(self, include_completed=True):
        """获取所有待办"""
        session = self.session
        try:
            query = session.query(Todo).options(
                joinedload(Todo.category),
                joinedload(Todo.tags)
            )
            if not include_completed:
                query = query.filter(Todo.completed == False)
            return query.order_by(
                Todo.completed,
                Todo.priority,
                Todo.created_at.desc()
            ).all()
        finally:
            session.close()

    def get_todo(self, todo_id):
        """获取单个待办"""
        session = self.session
        try:
            return session.query(Todo).options(
                joinedload(Todo.category),
                joinedload(Todo.tags)
            ).filter(Todo.id == todo_id).first()
        finally:
            session.close()

    def search_todos(self, keyword, category_id=None, tag_id=None, include_completed=True):
        """搜索待办"""
        session = self.session
        try:
            query = session.query(Todo).options(
                joinedload(Todo.category),
                joinedload(Todo.tags)
            )

            if not include_completed:
                query = query.filter(Todo.completed == False)

            if keyword:
                query = query.filter(
                    or_(
                        Todo.title.contains(keyword),
                        Todo.description.contains(keyword)
                    )
                )

            if category_id:
                query = query.filter(Todo.category_id == category_id)

            if tag_id:
                query = query.join(TodoTag).filter(TodoTag.tag_id == tag_id)

            return query.order_by(
                Todo.completed,
                Todo.priority,
                Todo.created_at.desc()
            ).all()
        finally:
            session.close()

    def get_todos_to_remind(self):
        """获取需要提醒的待办"""
        session = self.session
        try:
            now = datetime.now()
            return session.query(Todo).options(
                joinedload(Todo.category),
                joinedload(Todo.tags)
            ).filter(
                and_(
                    Todo.completed == False,
                    Todo.reminder_time != None,
                    Todo.reminder_time <= now
                )
            ).all()
        finally:
            session.close()

    def get_recurring_todos_for_today(self):
        """获取今天需要循环提醒的待办"""
        session = self.session
        try:
            now = datetime.now()
            today = date.today()

            todos = session.query(Todo).options(
                joinedload(Todo.category),
                joinedload(Todo.tags)
            ).filter(
                and_(
                    Todo.completed == False,
                    Todo.is_recurring == True,
                    Todo.recurring_time != None
                )
            ).all()

            result = []
            for todo in todos:
                if todo.should_remind_today():
                    # 检查时间是否已过
                    from datetime import datetime as dt
                    remind_dt = dt.combine(today, todo.recurring_time)
                    if remind_dt <= now:
                        result.append(todo)

            return result
        finally:
            session.close()

    def create_todo(self, title, description="", priority=PRIORITY_MEDIUM,
                    category_id=None, reminder_time=None, tag_ids=None,
                    is_recurring=False, recurring_type=None, recurring_time=None,
                    recurring_weekdays=None, exclude_holidays=False, holiday_list=None):
        """创建待办"""
        session = self.session
        try:
            todo = Todo(
                title=title,
                description=description,
                priority=priority,
                category_id=category_id,
                reminder_time=reminder_time,
                is_recurring=is_recurring,
                recurring_type=recurring_type,
                recurring_time=recurring_time,
                exclude_holidays=exclude_holidays
            )

            if recurring_weekdays is not None:
                todo.set_recurring_weekdays(recurring_weekdays)

            if holiday_list:
                todo.set_holidays(holiday_list)

            if tag_ids:
                tags = session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
                todo.tags = tags

            session.add(todo)
            session.flush()  # 刷新以获取ID
            todo_id = todo.id
            session.commit()
            return todo_id
        finally:
            session.close()

    def update_todo(self, todo_id, **kwargs):
        """更新待办"""
        session = self.session
        try:
            todo = session.query(Todo).filter(Todo.id == todo_id).first()
            if todo:
                for key, value in kwargs.items():
                    setattr(todo, key, value)
                session.commit()
            return todo
        finally:
            session.close()

    def complete_todo(self, todo_id):
        """完成待办"""
        return self.update_todo(todo_id, completed=True, completed_at=datetime.now())

    def uncomplete_todo(self, todo_id):
        """取消完成"""
        return self.update_todo(todo_id, completed=False, completed_at=None)

    def delete_todo(self, todo_id):
        """删除待办"""
        session = self.session
        try:
            todo = session.query(Todo).filter(Todo.id == todo_id).first()
            if todo:
                session.delete(todo)
                session.commit()
        finally:
            session.close()

    def batch_complete(self, todo_ids):
        """批量完成"""
        session = self.session
        try:
            session.query(Todo).filter(Todo.id.in_(todo_ids)).update(
                {Todo.completed: True, Todo.completed_at: datetime.now()},
                synchronize_session=False
            )
            session.commit()
        finally:
            session.close()

    def batch_delete(self, todo_ids):
        """批量删除"""
        session = self.session
        try:
            session.query(Todo).filter(Todo.id.in_(todo_ids)).delete(
                synchronize_session=False
            )
            session.commit()
        finally:
            session.close()

    def snooze_reminder(self, todo_id, minutes):
        """稍后提醒"""
        from datetime import timedelta
        new_time = datetime.now() + timedelta(minutes=minutes)
        return self.update_todo(todo_id, reminder_time=new_time)

    # ========== Category 操作 ==========

    def get_all_categories(self):
        """获取所有分类"""
        session = self.session
        try:
            return session.query(Category).order_by(Category.name).all()
        finally:
            session.close()

    def create_category(self, name, color="#4A90D9"):
        """创建分类"""
        session = self.session
        try:
            cat = Category(name=name, color=color)
            session.add(cat)
            session.commit()
            return cat
        finally:
            session.close()

    def delete_category(self, category_id):
        """删除分类"""
        session = self.session
        try:
            cat = session.query(Category).filter(Category.id == category_id).first()
            if cat:
                session.delete(cat)
                session.commit()
        finally:
            session.close()

    # ========== Tag 操作 ==========

    def get_all_tags(self):
        """获取所有标签"""
        session = self.session
        try:
            return session.query(Tag).order_by(Tag.name).all()
        finally:
            session.close()

    def create_tag(self, name):
        """创建标签"""
        session = self.session
        try:
            tag = Tag(name=name)
            session.add(tag)
            session.commit()
            return tag
        finally:
            session.close()

    def update_tag(self, tag_id, name):
        """更新标签"""
        session = self.session
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                tag.name = name
                session.commit()
            return tag
        finally:
            session.close()

    def delete_tag(self, tag_id):
        """删除标签"""
        session = self.session
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                session.delete(tag)
                session.commit()
        finally:
            session.close()

    # ========== Holiday 操作 ==========

    def get_all_holidays(self):
        """获取所有假期"""
        session = self.session
        try:
            return session.query(Holiday).order_by(Holiday.date).all()
        finally:
            session.close()

    def add_holiday(self, holiday_date, name=""):
        """添加假期"""
        session = self.session
        try:
            holiday = Holiday(date=holiday_date, name=name)
            session.add(holiday)
            session.commit()
            return holiday
        finally:
            session.close()

    def remove_holiday(self, holiday_id):
        """删除假期"""
        session = self.session
        try:
            holiday = session.query(Holiday).filter(Holiday.id == holiday_id).first()
            if holiday:
                session.delete(holiday)
                session.commit()
        finally:
            session.close()

    def is_holiday(self, check_date):
        """检查是否是假期"""
        session = self.session
        try:
            return session.query(Holiday).filter(Holiday.date == check_date).first() is not None
        finally:
            session.close()

    # ========== 统计 ==========

    def get_stats(self):
        """获取统计信息"""
        session = self.session
        try:
            total = session.query(Todo).count()
            completed = session.query(Todo).filter(Todo.completed == True).count()
            pending = total - completed
            overdue = session.query(Todo).filter(
                and_(
                    Todo.completed == False,
                    Todo.reminder_time != None,
                    Todo.reminder_time < datetime.now()
                )
            ).count()
            return {
                "total": total,
                "completed": completed,
                "pending": pending,
                "overdue": overdue
            }
        finally:
            session.close()


# 全局数据库实例
db = Database()
