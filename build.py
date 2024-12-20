import PyInstaller.__main__
import os
import sys
import subprocess

def install_requirements():
    """安装所需的依赖"""
    print("正在安装依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_build():
    """创建可执行文件"""
    print("正在打包程序...")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 先创建图标
    if not os.path.exists('icon.ico'):
        from create_icon import create_icon
        create_icon()
    
    # PyInstaller 配置
    PyInstaller.__main__.run([
        'image_metadata_editor_gui.py',  # 主程序文件
        '--name=图片元数据编辑器',  # 应用程序名称
        '--windowed',  # 使用 GUI 模式
        '--onefile',  # 打包成单个文件
        '--icon=icon.ico',  # 使用生成的图标
        '--add-data=README.txt;.',  # 添加说明文件
        '--clean',  # 清理临时文件
        f'--distpath={os.path.join(current_dir, "dist")}',  # 输出目录
        '--noconfirm',  # 不确认覆盖
        '--hidden-import=piexif',  # 添加 piexif 依赖
        '--hidden-import=PIL',  # 添加 PIL 依赖
        '--hidden-import=PIL.Image',  # 添加 PIL.Image 依赖
        '--log-level=INFO',  # 显示详细日志
    ])

def main():
    try:
        # 安装依赖
        install_requirements()
        
        # 创建构建
        create_build()
        
        print("\n打包完成！")
        print(f"可执行文件位置: {os.path.abspath('dist/图片元数据编辑器.exe')}")
        
        # 询问是否打开输出目录
        if input("\n是否打开输出目录？(y/n): ").lower() == 'y':
            os.startfile('dist')
            
    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("\n按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main() 