# TodoX - 待办事项提醒工具

一个基于 Python tkinter 的待办事项管理工具，支持提醒、分类、标签、循环提醒等功能。

## 功能特性

- 待办管理：添加、编辑、删除、完成待办事项
- 分类管理：按分类组织待办
- 标签管理：使用标签标记待办
- 优先级：高、中、低三级优先级
- 提醒功能：定时提醒、稍后提醒（2/5/10/15/30分钟）
- 循环提醒：每天、每周循环提醒
- 系统托盘：最小化到托盘运行
- 单实例运行：防止重复启动

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 打包发布

```bash
python build.py
```

输出目录：`dist\TodoX\TodoX.exe`

## 项目结构

```
TodoX/
├── main.py              # 程序入口
├── build.py             # 打包脚本
├── build.spec           # PyInstaller 配置
├── requirements.txt     # 依赖列表
├── .gitignore           # Git 忽略配置
├── README.md            # 说明文档
├── app/
│   ├── database.py      # 数据库操作
│   ├── reminder.py      # 提醒服务
│   └── ui/
│       ├── main_window.py   # 主窗口
│       ├── todo_list.py     # 待办列表
│       ├── todo_form.py     # 待办表单
│       ├── notification.py  # 提醒弹窗
│       ├── tray_icon.py     # 系统托盘
│       └── styles.py        # 样式配置
└── data/                # 数据存储目录
```

## 系统要求

- Windows 10+
- Python 3.10+
