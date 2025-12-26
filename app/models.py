"""数据库模型定义"""
from datetime import datetime, time, date
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Time, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()

# 优先级常量
PRIORITY_HIGH = 1
PRIORITY_MEDIUM = 2
PRIORITY_LOW = 3

PRIORITY_MAP = {
    1: "高",
    2: "中",
    3: "低"
}

# 循环类型常量
RECURRING_NONE = None
RECURRING_DAILY = "daily"
RECURRING_WEEKLY = "weekly"
RECURRING_MONTHLY = "monthly"

RECURRING_TYPES = {
    None: "不循环",
    RECURRING_DAILY: "每天",
    RECURRING_WEEKLY: "每周",
    RECURRING_MONTHLY: "每月"
}


class Category(Base):
    """分类表"""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(20), default="#4A90D9")

    todos = relationship("Todo", back_populates="category", lazy="dynamic")


class Tag(Base):
    """标签表"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    color = Column(String(20), default="#FF9800")

    todos = relationship("Todo", secondary="todo_tags", back_populates="tags")


class TodoTag(Base):
    """待办-标签关联表"""
    __tablename__ = 'todo_tags'

    todo_id = Column(Integer, ForeignKey('todos.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)


class Todo(Base):
    """待办事项表"""
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    priority = Column(Integer, default=PRIORITY_MEDIUM)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)

    # 提醒时间（可选）
    reminder_time = Column(DateTime, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)

    # 完成状态
    completed = Column(Boolean, default=False)

    # 循环提醒字段
    is_recurring = Column(Boolean, default=False)
    recurring_type = Column(String(20), nullable=True)  # daily, weekly
    recurring_time = Column(Time, nullable=True)
    recurring_weekdays = Column(Text, default="[]")  # JSON格式的周几 [0-6]
    exclude_holidays = Column(Boolean, default=False)
    holiday_json = Column(Text, default="[]")  # JSON格式的假期日期列表

    # 关系
    category = relationship("Category", back_populates="todos")
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")

    @property
    def priority_text(self):
        return PRIORITY_MAP.get(self.priority, "中")

    @property
    def recurring_type_text(self):
        return RECURRING_TYPES.get(self.recurring_type, "不循环")

    @property
    def tag_names(self):
        return [tag.name for tag in self.tags]

    def get_holidays(self):
        """获取假期日期列表"""
        import json
        try:
            return json.loads(self.holiday_json)
        except:
            return []

    def set_holidays(self, holidays):
        """设置假期日期列表"""
        import json
        self.holiday_json = json.dumps(holidays)

    def get_recurring_weekdays(self):
        """获取循环提醒的周几列表"""
        import json
        try:
            return json.loads(self.recurring_weekdays)
        except:
            return []

    def set_recurring_weekdays(self, weekdays):
        """设置循环提醒的周几列表"""
        import json
        self.recurring_weekdays = json.dumps(weekdays)

    def should_remind_today(self):
        """检查今天是否应该提醒（考虑循环和假期）"""
        if self.completed:
            return False

        if not self.is_recurring or not self.recurring_time:
            return False

        today = date.today()

        # 检查周几（Python weekday()返回0-6，对应周一到周日）
        # 用户界面存储的是0-6（周一=0）
        if self.recurring_type == "weekly":
            weekdays = self.get_recurring_weekdays()
            if weekdays:
                # Python weekday(): Monday=0, Sunday=6
                # 存储的也是0-6
                if today.weekday() not in weekdays:
                    return False

        # 检查是否是假期
        if self.exclude_holidays:
            holidays = self.get_holidays()
            if today.isoformat() in holidays:
                return False

        return True


class Holiday(Base):
    """假期配置表"""
    __tablename__ = 'holidays'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True)
    name = Column(String(100), nullable=True)

    @classmethod
    def is_holiday(cls, session, check_date):
        """检查指定日期是否是假期"""
        holiday = session.query(cls).filter(cls.date == check_date).first()
        return holiday is not None


def get_database_path():
    """获取数据库文件路径"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', 'todo.db')


def init_database():
    """初始化数据库"""
    engine = create_engine(
        f'sqlite:///{get_database_path()}',
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )
    Base.metadata.create_all(engine)
    return engine
