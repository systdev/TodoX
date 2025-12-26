"""
TodoX 构建脚本
将应用打包为目录形式的 Windows 可执行文件

使用方法:
    python build.py

要求:
    pip install pyinstaller pillow

注意: 使用目录模式（--onedir）比单文件模式（--onefile）启动更快
"""

import os
import sys
import shutil

def clean_build_dirs():
    """清理构建目录"""
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理: {dir_name}")

def build_exe():
    """构建 exe"""
    cmd = [
        'pyinstaller',
        '--name=TodoX',
        '--onedir',            # 目录模式（启动更快）
        '--windowed',          # 无控制台窗口
        '--clean',             # 清理缓存
        '--noconfirm',         # 不确认覆盖
    ]

    # 添加图标（如果存在）
    icon_path = 'data/icon.ico'
    if os.path.exists(icon_path):
        cmd.append(f'--icon={icon_path}')

    # 添加数据文件
    cmd.append('--add-data=data;.\\data')

    # 指定入口文件
    cmd.append('main.py')

    # 执行构建
    print("开始构建...")
    result = os.system(' '.join(cmd))

    if result == 0:
        print("\n构建成功!")
        print(f"输出目录: {os.path.abspath('dist\\TodoX')}")
        print("\n运行命令: dist\\TodoX\\TodoX.exe")
    else:
        print("\n构建失败!")
        sys.exit(1)

def main():
    """主函数"""
    print("=" * 50)
    print("TodoX 构建脚本")
    print("=" * 50)

    # 检查是否安装了 pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("未安装 PyInstaller，正在安装...")
        os.system('pip install pyinstaller pillow')
        print("安装完成!\n")

    # 清理旧构建
    print("\n清理旧的构建文件...")
    clean_build_dirs()

    # 构建
    build_exe()

    print("\n" + "=" * 50)
    print("完成!")
    print("=" * 50)

if __name__ == '__main__':
    main()
