import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from image_metadata_editor import ImageMetadataEditor
import os
from PIL import Image
import concurrent.futures
from queue import Queue
import threading
import random
from datetime import datetime, timedelta

class ImageMetadataEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片元数据编辑器")
        
        # 初始化变量
        self.editor = None
        self.batch_files = []  # 存储批量处理的文件列表
        self.pending_operations = {}  # 存储待执行的操作
        
        # 设置最小窗口大小
        self.root.minsize(900, 600)
        
        # 配置根窗口的网格权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主框架的网格权重
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # 
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 单文件处理页面
        self.single_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.single_frame, text="单文件处理")
        
        # 配置单文件页面的网格权重
        self.single_frame.grid_rowconfigure(1, weight=1)  # 元数据显示区域可扩展
        self.single_frame.grid_columnconfigure(0, weight=1)
        
        # 批量处理页面
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="批量处理")
        
        # 配置批量处理页面的网格权重
        self.batch_frame.grid_rowconfigure(0, weight=1)
        self.batch_frame.grid_columnconfigure(0, weight=1)
        
        # 设置单文件处理界面
        self.setup_single_file_ui()
        
        # 设置批量处理界面
        self.setup_batch_file_ui()
        
        # 添加线程池和处理队列
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.processing_queue = Queue()
        self.processing_results = {}

    def setup_single_file_ui(self):
        """单文件处理界面"""
        # 文件选择部分
        self.file_frame = ttk.LabelFrame(self.single_frame, text="图片选择", padding="5")
        self.file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 配置文件选择框架的网格权重
        self.file_frame.grid_columnconfigure(0, weight=1)
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        self.browse_button = ttk.Button(self.file_frame, text="浏览", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=5)
        
        # 元数据显示部分
        self.metadata_frame = ttk.LabelFrame(self.single_frame, text="元数据信息", padding="5")
        self.metadata_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 配置元数据框架的网格权重
        self.metadata_frame.grid_columnconfigure(0, weight=1)
        self.metadata_frame.grid_rowconfigure(0, weight=1)
        
        # 创建表格来显示元数据
        self.tree = ttk.Treeview(self.metadata_frame, columns=('标签', '值'), show='headings')
        self.tree.heading('标签', text='标签')
        self.tree.heading('值', text='值')
        self.tree.column('标签', width=150, minwidth=100)
        self.tree.column('值', width=450, minwidth=200)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.metadata_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 操作按钮部分
        self.button_frame = ttk.LabelFrame(self.single_frame, text="操作", padding="5")
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 第一行按钮
        self.button_frame1 = ttk.Frame(self.button_frame)
        self.button_frame1.grid(row=0, column=0, pady=5)
        
        self.refresh_button = ttk.Button(self.button_frame1, text="刷新元数据", width=20, command=self.refresh_metadata)
        self.refresh_button.grid(row=0, column=0, padx=5)
        
        self.strip_button = ttk.Button(self.button_frame1, text="清除原图元数据", width=20, command=self.strip_all_metadata)
        self.strip_button.grid(row=0, column=1, padx=5)
        
        # 第二行按钮
        self.button_frame2 = ttk.Frame(self.button_frame)
        self.button_frame2.grid(row=1, column=0, pady=5)
        
        self.save_as_button = ttk.Button(
            self.button_frame2, 
            text="另存为新文件（无元数据）", 
            width=42,
            command=self.save_clean_copy
        )
        self.save_as_button.grid(row=0, column=0, columnspan=2, padx=5)
        
        # 添加提示标签
        self.tip_label = ttk.Label(
            self.button_frame, 
            text='提示：建议使用"另存为新文件"功能，这样可以保留原图',
            foreground="gray"
        )
        self.tip_label.grid(row=2, column=0, pady=(5,0))
        
        # 添加元数据编辑区域
        self.edit_frame = ttk.LabelFrame(self.single_frame, text="编辑元数据", padding="5")
        self.edit_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 添加手机型号预设选择
        preset_frame = ttk.Frame(self.edit_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(preset_frame, text="预设手机型号:").pack(side=tk.LEFT, padx=5)
        
        # 手机预设信息
        self.phone_presets = {
            "不使用预设": {},
            "iPhone 12": {
                "Make": "Apple",
                "Model": "iPhone 12",
                "Software": "iOS 15.0",
                "DateTime": "2024:01:20 15:30:00",
                "DateTimeOriginal": "2024:01:20 15:30:00",
                "DateTimeDigitized": "2024:01:20 15:30:00",
                "ExifVersion": b"0232",
                "ComponentsConfiguration": b"\x01\x02\x03\x00",
                "ShutterSpeedValue": (7022, 1000),
                "ApertureValue": (16, 10),
                "ExposureTime": (1, 60),
                "FNumber": (16, 10),
                "ExposureProgram": 2,
                "ISOSpeedRatings": 32,
                "ExifImageWidth": 4032,
                "ExifImageHeight": 3024,
                "FocalLength": (42, 10),
                "FocalLengthIn35mmFilm": 26,
                "ColorSpace": 1,
                "WhiteBalance": 0,
                "BrightnessValue": (578, 100),
                "MeteringMode": 5,
                "Flash": 16,
                "SubjectArea": (2015, 1511, 2217, 1330),
                "SensingMethod": 2,
                "SceneType": b"\x01",
                "ExposureMode": 0,
                "DigitalZoomRatio": (1, 1),
                "SceneCaptureType": 0,
                "LensSpecification": ((154, 100), (789, 100), (16, 10), (24, 10)),
                "LensMake": "Apple",
                "LensModel": "iPhone 12 back dual wide camera 4.2mm f/1.6"
            },
            "iPhone 13 Pro Max": {
                "Make": "Apple",
                "Model": "iPhone 13 Pro Max",
                "Software": "iOS 16.0",
                "DateTime": "2024:01:20 15:30:00",
                "DateTimeOriginal": "2024:01:20 15:30:00",
                "DateTimeDigitized": "2024:01:20 15:30:00",
                "ExifVersion": b"0232",
                "ComponentsConfiguration": b"\x01\x02\x03\x00",
                "ShutterSpeedValue": (8022, 1000),
                "ApertureValue": (15, 10),
                "ExposureTime": (1, 120),
                "FNumber": (15, 10),
                "ExposureProgram": 2,
                "ISOSpeedRatings": 40,
                "ExifImageWidth": 4032,
                "ExifImageHeight": 3024,
                "FocalLength": (57, 10),
                "FocalLengthIn35mmFilm": 35,
                "ColorSpace": 1,
                "WhiteBalance": 0,
                "BrightnessValue": (612, 100),
                "MeteringMode": 5,
                "Flash": 16,
                "SubjectArea": (2015, 1511, 2217, 1330),
                "SensingMethod": 2,
                "SceneType": b"\x01",
                "ExposureMode": 0,
                "DigitalZoomRatio": (1, 1),
                "SceneCaptureType": 0,
                "LensSpecification": ((154, 100), (789, 100), (15, 10), (28, 10)),
                "LensMake": "Apple",
                "LensModel": "iPhone 13 Pro Max back triple camera 5.7mm f/1.5"
            },
            "Samsung Galaxy S21 Ultra": {
                "Make": "SAMSUNG",
                "Model": "SM-G998B",
                "Software": "G998BXXU3BUK8",
                "DateTime": "2024:01:20 15:30:00",
                "DateTimeOriginal": "2024:01:20 15:30:00",
                "DateTimeDigitized": "2024:01:20 15:30:00",
                "ExifVersion": b"0220",
                "ComponentsConfiguration": b"\x01\x02\x03\x00",
                "ShutterSpeedValue": (6643, 1000),
                "ApertureValue": (18, 10),
                "ExposureTime": (1, 100),
                "FNumber": (18, 10),
                "ExposureProgram": 2,
                "ISOSpeedRatings": 50,
                "ExifImageWidth": 4000,
                "ExifImageHeight": 3000,
                "FocalLength": (67, 10),
                "FocalLengthIn35mmFilm": 24,
                "ColorSpace": 1,
                "WhiteBalance": 0,
                "BrightnessValue": (745, 100),
                "MeteringMode": 2,
                "Flash": 0,
                "SubjectArea": (2000, 1500, 2200, 1320),
                "SensingMethod": 2,
                "SceneType": b"\x01",
                "ExposureMode": 0,
                "DigitalZoomRatio": (1, 1),
                "SceneCaptureType": 0,
                "LensSpecification": ((154, 100), (989, 100), (18, 10), (24, 10)),
                "LensMake": "Samsung",
                "LensModel": "Samsung S5KHM3 24mm f/1.8"
            },
            "Xiaomi 12 Pro": {
                "Make": "Xiaomi",
                "Model": "2201122C",
                "Software": "MIUI 13",
                "DateTime": "2024:01:20 15:30:00",
                "DateTimeOriginal": "2024:01:20 15:30:00",
                "DateTimeDigitized": "2024:01:20 15:30:00",
                "ExifVersion": b"0220",
                "ComponentsConfiguration": b"\x01\x02\x03\x00",
                "ShutterSpeedValue": (6022, 1000),
                "ApertureValue": (19, 10),
                "ExposureTime": (1, 90),
                "FNumber": (19, 10),
                "ExposureProgram": 2,
                "ISOSpeedRatings": 64,
                "ExifImageWidth": 4096,
                "ExifImageHeight": 3072,
                "FocalLength": (50, 10),
                "FocalLengthIn35mmFilm": 24,
                "ColorSpace": 1,
                "WhiteBalance": 0,
                "BrightnessValue": (812, 100),
                "MeteringMode": 5,
                "Flash": 0,
                "SubjectArea": (2048, 1536, 2200, 1350),
                "SensingMethod": 2,
                "SceneType": b"\x01",
                "ExposureMode": 0,
                "DigitalZoomRatio": (1, 1),
                "SceneCaptureType": 0,
                "LensSpecification": ((154, 100), (789, 100), (19, 10), (24, 10)),
                "LensMake": "Sony",
                "LensModel": "Sony IMX707 24mm f/1.9"
            }
        }
        
        self.preset_var = tk.StringVar(value="不使用预设")
        preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=list(self.phone_presets.keys()),
            width=20,
            state="readonly"
        )
        preset_combo.pack(side=tk.LEFT, padx=5)
        
        # 添加应用预设按钮
        ttk.Button(
            preset_frame,
            text="应用预设",
            command=self.apply_phone_preset
        ).pack(side=tk.LEFT, padx=5)
        
        # 创建编辑字段
        fields_frame = ttk.Frame(self.edit_frame)
        fields_frame.pack(fill=tk.X, expand=True)
        
        # 常用EXIF字段
        self.metadata_fields = {
            'Artist': tk.StringVar(),  # 作者
            'Copyright': tk.StringVar(),  # 版权
            'ImageDescription': tk.StringVar(),  # 图片描述
            'Make': tk.StringVar(),  # 相机制造商
            'Model': tk.StringVar(),  # 相机型号
            'Software': tk.StringVar(),  # 软件
            'DateTime': tk.StringVar(),  # 拍摄时间
            'GPSLatitude': tk.StringVar(),  # GPS纬度
            'GPSLongitude': tk.StringVar(),  # GPS经度
        }
        
        # 创建编辑界面
        row = 0
        col = 0
        for field, var in self.metadata_fields.items():
            frame = ttk.Frame(fields_frame)
            frame.grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
            
            ttk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            ttk.Entry(frame, textvariable=var, width=20).pack(side=tk.LEFT, padx=5)
            
            col += 1
            if col > 2:  # 每行显示3个字段
                col = 0
                row += 1
        
        # 添加按钮
        button_frame = ttk.Frame(self.edit_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="更新元数据",
            command=self.update_metadata
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="清空字段",
            command=self.clear_metadata_fields
        ).pack(side=tk.LEFT, padx=5)

    def setup_batch_file_ui(self):
        """设置批量处理界面"""
        # 设置batch_frame的列重
        self.batch_frame.grid_columnconfigure(0, weight=3)  # 文件列表占更多空间
        self.batch_frame.grid_columnconfigure(1, weight=1)  # 控制面板占较少空间
        self.batch_frame.grid_rowconfigure(0, weight=1)  # 让主内容区域可以扩展
        
        # 左侧：文件列表框架
        self.files_frame = ttk.LabelFrame(self.batch_frame, text="待处理文件列表", padding="5")
        self.files_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # 让件列表框架可以扩
        self.files_frame.grid_columnconfigure(0, weight=1)
        self.files_frame.grid_rowconfigure(0, weight=1)
        
        # 创建文件列表 - 修复列名称
        self.files_tree = ttk.Treeview(self.files_frame, columns=('文件名', '大小', '状态'), show='headings')
        self.files_tree.heading('文件名', text='文件名')  # 确保这里的列名与创建时完全��致
        self.files_tree.heading('大小', text='大小')
        self.files_tree.heading('状态', text='状态')
        
        # 调整列宽和最小宽度
        self.files_tree.column('文件名', width=400, minwidth=200)
        self.files_tree.column('大小', width=80, minwidth=80)
        self.files_tree.column('状态', width=300, minwidth=200)
        
        self.files_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加垂直滚动条
        scrollbar_y = ttk.Scrollbar(self.files_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 添加水平滚动条
        scrollbar_x = ttk.Scrollbar(self.files_frame, orient=tk.HORIZONTAL, command=self.files_tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 配置滚动条
        self.files_tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # 右侧：操作按钮区域
        self.batch_controls = ttk.Frame(self.batch_frame)
        self.batch_controls.grid(row=0, column=1, padx=10, sticky=(tk.N, tk.S))
        
        # 文件操作按钮组
        self.file_ops = ttk.LabelFrame(self.batch_controls, text="文件操作", padding="5")
        self.file_ops.pack(fill=tk.X, pady=5)
        
        ttk.Button(self.file_ops, text="添加文件", command=self.add_files).pack(fill=tk.X, pady=2)
        ttk.Button(self.file_ops, text="添加文件夹", command=self.add_folder).pack(fill=tk.X, pady=2)
        ttk.Button(self.file_ops, text="移除选中", command=self.remove_selected).pack(fill=tk.X, pady=2)
        ttk.Button(self.file_ops, text="清空列表", command=self.clear_file_list).pack(fill=tk.X, pady=2)
        
        # 批量处理按钮组
        self.batch_ops = ttk.LabelFrame(self.batch_controls, text="操作选择", padding="5")
        self.batch_ops.pack(fill=tk.X, pady=5)
        
        # 清除元数据选项
        self.clear_metadata_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.batch_ops, 
            text="清除元数据",  # 修正文字显示
            variable=self.clear_metadata_var
        ).pack(fill=tk.X, pady=2)
        
        # 调整尺寸选项框
        self.resize_frame = ttk.LabelFrame(self.batch_controls, text="调整尺寸", padding="5")
        self.resize_frame.pack(fill=tk.X, pady=5)
        
        # 启用调整尺寸选项
        self.resize_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.resize_frame,
            text="启用尺寸调整",
            variable=self.resize_enabled_var
        ).pack(fill=tk.X, pady=2)
        
        # 预设分辨率选择
        preset_frame = ttk.Frame(self.resize_frame)
        preset_frame.pack(fill=tk.X, pady=2)
        ttk.Label(preset_frame, text="预设:").pack(side=tk.LEFT, padx=5)
        
        # 预设分辨率选项（横向）
        resolutions_landscape = {
            "自定义": (0, 0),
            "540p": (960, 540),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "2K": (2048, 1080),
            "2160p": (3840, 2160),
            "4K": (4096, 2160)
        }
        
        # 预设分辨率选项（竖向）
        resolutions_portrait = {
            "自定义": (0, 0),
            "540p": (540, 960),
            "720p": (720, 1280),
            "1080p": (1080, 1920),
            "2K": (1080, 2048),
            "2160p": (2160, 3840),
            "4K": (2160, 4096)
        }
        
        # 横选择
        self.orientation_var = tk.StringVar(value="横向")
        ttk.Radiobutton(
            preset_frame,
            text="横向",
            variable=self.orientation_var,
            value="横向"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            preset_frame,
            text="竖向",
            variable=self.orientation_var,
            value="竖向"
        ).pack(side=tk.LEFT)
        
        self.resolution_var = tk.StringVar(value="自定义")
        resolution_combo = ttk.Combobox(
            preset_frame, 
            textvariable=self.resolution_var,
            values=list(resolutions_landscape.keys()),
            width=10,
            state="readonly"
        )
        resolution_combo.pack(side=tk.LEFT, padx=5)
        
        # 宽度输入框架
        width_frame = ttk.Frame(self.resize_frame)
        width_frame.pack(fill=tk.X, pady=2)
        ttk.Label(width_frame, text="宽度:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.StringVar(value="1920")
        self.width_entry = ttk.Entry(width_frame, textvariable=self.width_var, width=8)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        
        # 高度输入框架
        height_frame = ttk.Frame(self.resize_frame)
        height_frame.pack(fill=tk.X, pady=2)
        ttk.Label(height_frame, text="高度:").pack(side=tk.LEFT, padx=5)
        self.height_var = tk.StringVar(value="1080")
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=8)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        
        # 保持比例选项
        self.keep_ratio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.resize_frame, 
            text="保持宽高比", 
            variable=self.keep_ratio_var
        ).pack(fill=tk.X, pady=2)
        
        # 裁剪选项
        crop_frame = ttk.Frame(self.resize_frame)
        crop_frame.pack(fill=tk.X, pady=2)

        self.crop_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            crop_frame,
            text="启用裁剪",
            variable=self.crop_enabled_var
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(crop_frame, text="裁剪位置:").pack(side=tk.LEFT, padx=5)
        self.crop_position_var = tk.StringVar(value="居中")
        crop_position_combo = ttk.Combobox(
            crop_frame,
            textvariable=self.crop_position_var,
            values=["居中", "左上角", "右上角", "左下角", "右下角"],
            width=8,
            state="readonly"
        )
        crop_position_combo.pack(side=tk.LEFT, padx=5)

        # 裁剪位置映射
        self.crop_position_map = {
            "居中": "center",
            "左上角": "top_left",
            "右上角": "top_right",
            "左下": "bottom_left",
            "右下角": "bottom_right"
        }
        
        # 绑定预设分辨率选择事件
        def on_resolution_change(event=None):
            selected = self.resolution_var.get()
            resolutions = resolutions_landscape if self.orientation_var.get() == "横向" else resolutions_portrait
            
            if selected == "自定义":
                self.width_entry.config(state="normal")
                self.height_entry.config(state="normal")
            else:
                width, height = resolutions[selected]
                self.width_var.set(str(width))
                self.height_var.set(str(height))
                self.width_entry.config(state="readonly")
                self.height_entry.config(state="readonly")
        
        # 绑定横竖选择事件
        def on_orientation_change(*args):
            current_preset = self.resolution_var.get()
            if current_preset != "自定义":
                on_resolution_change()
        
        resolution_combo.bind('<<ComboboxSelected>>', on_resolution_change)
        self.orientation_var.trace('w', on_orientation_change)
        
        # 替换原来的处理按钮，改为另存为按钮
        self.save_frame = ttk.LabelFrame(self.batch_controls, text="保存", padding="5")
        self.save_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            self.save_frame,
            text="另存为新文件",
            command=self.batch_save_as
        ).pack(fill=tk.X, pady=2)
        
        # 进度显示框架调整
        self.progress_frame = ttk.LabelFrame(self.batch_frame, text="处理进度", padding="5")
        self.progress_frame.grid(
            row=1, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), 
            pady=5, padx=5
        )
        
        # 让进度条框架可以水平扩展
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.grid(
            row=0, column=0, 
            sticky=(tk.W, tk.E), 
            padx=5, pady=5
        )
        
        self.progress_label = ttk.Label(self.progress_frame, text="就绪")
        self.progress_label.grid(
            row=1, column=0, 
            sticky=(tk.W), 
            padx=5, pady=(0,5)
        )
        
        # 添加批量元数据预设选项
        metadata_frame = ttk.LabelFrame(self.batch_frame, text="批量元数据设置", padding="5")
        metadata_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 添加预设选择
        preset_frame = ttk.Frame(metadata_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(preset_frame, text="预设手机型号:").pack(side=tk.LEFT, padx=5)
        
        self.batch_preset_var = tk.StringVar(value="不使用预设")
        preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.batch_preset_var,
            values=list(self.phone_presets.keys()),
            width=20,
            state="readonly"
        )
        preset_combo.pack(side=tk.LEFT, padx=5)
        
        # 添加元数据选项
        self.apply_metadata_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            metadata_frame,
            text="应用预设元数据",
            variable=self.apply_metadata_var
        ).pack(pady=2)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.file_path.set(filename)
            self.editor = ImageMetadataEditor(filename)
            self.refresh_metadata()

    def refresh_metadata(self):
        if not self.editor:
            messagebox.showwarning("警告", "请先选择图片文件！")
            return
            
        # 清空��有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 获取并示元数据
        metadata = self.editor.get_metadata()
        if isinstance(metadata, dict):
            for tag, value in metadata.items():
                self.tree.insert('', tk.END, values=(tag, value))
        else:
            messagebox.showinfo("提示", metadata)  # 显示错误信息
        
        # 更新编辑字段
        metadata = self.editor.get_metadata()
        if isinstance(metadata, dict):
            for field, var in self.metadata_fields.items():
                var.set(metadata.get(field, ""))

    def strip_all_metadata(self):
        """清除所有元数据"""
        if not self.editor:
            messagebox.showwarning("警告", "请先选择图片文件！")
            return
        
        if messagebox.askyesno("确认", "确定要清除所有元数据吗？此操作不可撤销！"):
            result = self.editor.strip_all_metadata()
            if result == True:
                # 验证清除结果
                if self.editor.verify_clean(self.file_path.get()):
                    messagebox.showinfo("成功", "所有元数据已完全清除！")
                else:
                    messagebox.showwarning("警告", "元��据已清除，但建议您检查结果或使用保存副本功能。")
                self.refresh_metadata()
            else:
                messagebox.showerror("错误", result)

    def save_clean_copy(self):
        """保存无元数据的副本（另存为）"""
        if not self.editor:
            messagebox.showwarning("警告", "请先选择图片文件！")
            return
        
        original_path = self.file_path.get()
        file_name, file_ext = os.path.splitext(original_path)
        new_path = f"{file_name}_无元数据{file_ext}"
        
        output_path = filedialog.asksaveasfilename(
            title="另存为（无元数据版本）",
            defaultextension=file_ext,
            initialfile=os.path.basename(new_path),
            filetypes=[
                ("JPEG图片", "*.jpg *.jpeg"),
                ("PNG图片", "*.png"),
                ("所有图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        
        if output_path:
            result = self.editor.save_clean_copy(output_path)
            if result == True:
                # 证新文件
                if self.editor.verify_clean(output_path):
                    messagebox.showinfo(
                        "��功", 
                        f"已成功保存无元数据版本到:\n{output_path}\n\n原图保持不变。"
                    )
                    # 询问是否开保存位置
                    if messagebox.askyesno("询问", "是否打开文件所在位置？"):
                        os.startfile(os.path.dirname(output_path))
                else:
                    messagebox.showwarning(
                        "警告", 
                        f"文件已保存，但建议您检查结果:\n{output_path}"
                    )
            else:
                messagebox.showerror("错误", result)

    def add_files(self):
        """添加多个文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        self._add_files_to_list(files)

    def _add_files_to_list(self, files):
        """将文件添加到列表中"""
        for file in files:
            if file not in self.batch_files:
                try:
                    size = os.path.getsize(file)
                    size_str = f"{size/1024/1024:.1f} MB" if size > 1024*1024 else f"{size/1024:.1f} KB"
                    self.batch_files.append(file)
                    self.files_tree.insert('', tk.END, values=(file, size_str, "待处理"))
                except Exception as e:
                    messagebox.showerror("错误", f"添加文件失败: {str(e)}")

    def add_folder(self):
        """添加文件夹中的所有图片"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                        file_path = os.path.join(root, file)
                        if file_path not in self.batch_files:
                            self.batch_files.append(file_path)
                            self.files_tree.insert('', tk.END, values=(file_path, "待处理"))

    def clear_file_list(self):
        """清空文件列表"""
        if messagebox.askyesno("确认", "确定要清空文件列表吗？"):
            self.batch_files.clear()
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)

    def remove_selected(self):
        """移除选中的文件"""
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要移除的文件！")
            return
        
        for item in selected:
            file_path = self.files_tree.item(item)['values'][0]
            self.batch_files.remove(file_path)
            self.files_tree.delete(item)

    def batch_save_as(self):
        """批量另存为处理"""
        if not self.batch_files:
            messagebox.showwarning("警告", "请先添加要处理的文件！")
            return
            
        # 检查是否选择了操作
        if not self.clear_metadata_var.get() and not self.resize_enabled_var.get():
            messagebox.showwarning("警告", "请至少选择一个操作！")
            return
            
        # 如果启用了尺寸调整，验证尺寸输入
        if self.resize_enabled_var.get():
            try:
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                if width <= 0 or height <= 0:
                    raise ValueError("尺寸必须大于0")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的尺寸数值！")
                return
        
        # 选择保存目录
        output_dir = filedialog.askdirectory(title="选择保存位置")
        if not output_dir:
            return
            
        total = len(self.batch_files)
        self.progress_bar['maximum'] = total
        self.progress_bar['value'] = 0
        
        # 创建处理任务
        futures = []
        for item in self.files_tree.get_children():
            file_path = self.files_tree.item(item)['values'][0]
            future = self.thread_pool.submit(
                self.process_single_image,
                file_path,
                output_dir,
                item
            )
            futures.append(future)
        
        # 启动进度更新线程
        threading.Thread(target=self.update_progress, args=(futures,), daemon=True).start()

    def process_single_image(self, file_path, output_dir, item):
        """在单独线程中处理单个图片"""
        original = None
        new_image = None
        try:
            # 初始化状态列表
            status = []
            
            # 构建新文件名
            file_name = os.path.basename(file_path)
            name, ext = os.path.splitext(file_name)
            
            operations = []
            if self.clear_metadata_var.get():
                operations.append("清除元数据")
                status.append("已清除元数据")

            if self.resize_enabled_var.get():
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                if self.crop_enabled_var.get():
                    operations.append(f"裁剪_{width}x{height}_{self.crop_position_var.get()}")
                    status.append(f"已裁剪至 {width}x{height}")
                else:
                    operations.append(f"调整尺寸_{width}x{height}")
                    status.append(f"已调整为 {width}x{height}")

            new_name = "_".join(operations) if operations else "processed"
            
            # 生成输出路径
            counter = 1
            base_path = os.path.join(output_dir, f"{new_name}_{name}{ext}")
            new_path = base_path
            while os.path.exists(new_path):
                new_path = os.path.join(output_dir, f"{new_name}_{name}_{counter}{ext}")
                counter += 1

            # 打开原始图片
            original = Image.open(file_path)
            original_format = original.format or 'JPEG'
            
            # 创建新图像（不带元数据）
            new_image = Image.new(original.mode, original.size)
            new_image.putdata(list(original.getdata()))
            
            # 如果需要调整尺寸
            if self.resize_enabled_var.get():
                # ... (调整尺寸的代码保持不变)
                pass

            # 保存图片（不带元数据）
            save_params = {
                'format': original_format,
                'quality': 95 if original_format == 'JPEG' else None,
            }
            
            if original_format == 'JPEG':
                save_params.update({
                    'optimize': False,
                    'exif': b"",
                    'icc_profile': None,
                    'comment': None,
                    'subsampling': -1,  # 使用默认的子采样
                    'qtables': None,    # 使用默认的量化表
                    'progressive': False,
                    'smooth': 0,
                    'streamtype': 0,    # 基本 JPEG
                    'dpi': (72, 72),    # 标准分辨率
                    'jfif': None,       # 不写入 JFIF 标记
                    'adobe': None       # 不写入 Adobe 标记
                })
            elif original_format == 'PNG':
                save_params.update({
                    'optimize': False,
                    'pnginfo': None
                })
            
            new_image.save(new_path, **save_params)
            
            # 如果需要应用元数据预设
            if self.apply_metadata_var.get() and self.batch_preset_var.get() != "不使用预设":
                try:
                    base_preset = self.phone_presets[self.batch_preset_var.get()]
                    dynamic_preset = self.generate_dynamic_preset(base_preset)
                    
                    temp_editor = ImageMetadataEditor(new_path)
                    temp_editor.update_metadata(dynamic_preset)
                    temp_editor.image.close()
                    status.append(f"已应用{self.batch_preset_var.get()}预设")
                except Exception as e:
                    return item, f"元数据应用失败: {str(e)}"

            return item, ", ".join(status) if status else "处理完成"
            
        except Exception as e:
            return item, f"错误: {str(e)}"
        finally:
            # 确保资源被释放
            if original:
                try:
                    original.close()
                except:
                    pass
            if new_image:
                try:
                    new_image.close()
                except:
                    pass

    def update_progress(self, futures):
        """更新进度条和状态"""
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            item, status = future.result()
            self.files_tree.set(item, '状态', status)
            completed += 1
            self.progress_bar['value'] = completed
            self.progress_label['text'] = f"已完成: {completed}/{len(futures)}"
            self.root.update()
        
        self.progress_label['text'] = "处理完成"
        messagebox.showinfo("完成", "所有文件处理完成！")

    def update_metadata(self):
        """更新图片元数据"""
        if not self.editor:
            messagebox.showwarning("警告", "请先选择图片文件！")
            return
        
        # 收集非空的元数据字段
        metadata = {}
        for field, var in self.metadata_fields.items():
            value = var.get().strip()
            if value:
                metadata[field] = value
        
        if not metadata:
            messagebox.showwarning("警告", "请至少填写一个字段！")
            return
        
        try:
            # 更新元数据
            result = self.editor.update_metadata(metadata)
            if result is True:
                messagebox.showinfo("成功", "元数据已更新！")
                self.refresh_metadata()  # 刷新显示
            else:
                messagebox.showerror("错误", str(result))
        except Exception as e:
            messagebox.showerror("错误", f"更新元数据失败: {str(e)}")

    def clear_metadata_fields(self):
        """清空所有元数据编辑字段"""
        for var in self.metadata_fields.values():
            var.set("")

    def generate_dynamic_preset(self, preset_base):
        """生成动态预设数据"""
        # 复制基础预设
        preset = preset_base.copy()
        
        # 生成随机时间（最近24小时内）
        random_time = datetime.now() - timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        time_str = random_time.strftime("%Y:%m:%d %H:%M:%S")
        preset["DateTime"] = time_str
        preset["DateTimeOriginal"] = time_str
        preset["DateTimeDigitized"] = time_str
        
        # 随机调整曝光参数
        if "ExposureTime" in preset:
            # 生成合理的快门速度变化
            shutter_speeds = [(1, 30), (1, 40), (1, 50), (1, 60), (1, 80), (1, 100), (1, 125), (1, 160)]
            preset["ExposureTime"] = random.choice(shutter_speeds)
            
        if "ISOSpeedRatings" in preset:
            # ISO通常会根据光线条件变化
            iso_values = [50, 64, 80, 100, 125, 160, 200, 250, 320]
            preset["ISOSpeedRatings"] = random.choice(iso_values)
        
        if "BrightnessValue" in preset:
            # 亮度值随机浮动
            base_brightness = preset["BrightnessValue"][0] / preset["BrightnessValue"][1]
            brightness_variation = random.uniform(-1.0, 1.0)
            new_brightness = int((base_brightness + brightness_variation) * 100)
            preset["BrightnessValue"] = (new_brightness, 100)
        
        # 随机调整对焦区域
        if "SubjectArea" in preset:
            base_x, base_y, base_w, base_h = preset["SubjectArea"]
            variation = 100  # 像素变化范围
            new_x = base_x + random.randint(-variation, variation)
            new_y = base_y + random.randint(-variation, variation)
            new_w = base_w + random.randint(-variation//2, variation//2)
            new_h = base_h + random.randint(-variation//2, variation//2)
            preset["SubjectArea"] = (new_x, new_y, new_w, new_h)
        
        # 随机调整白平衡
        if "WhiteBalance" in preset:
            # 偶尔使用手动白平衡
            preset["WhiteBalance"] = random.choice([0, 0, 0, 1])  # 80%概率使用自动白平衡
        
        return preset

    def apply_phone_preset(self):
        """应用手机预设信息"""
        if not self.editor:
            messagebox.showwarning("警告", "请先选择图片文件！")
            return
        
        selected_preset = self.preset_var.get()
        base_preset = self.phone_presets[selected_preset]
        
        if not base_preset:
            messagebox.showinfo("提示", "请选择一个手机型号预设")
            return
        
        try:
            # 生成动态预设数据
            dynamic_preset = self.generate_dynamic_preset(base_preset)
            
            # 应用预设
            result = self.editor.update_metadata(dynamic_preset)
            if result is True:
                messagebox.showinfo("成功", "预设元数据已应用！")
                self.refresh_metadata()  # 刷新显示
                
                # 更新编辑框中的显示
                for field, var in self.metadata_fields.items():
                    var.set(str(dynamic_preset.get(field, "")))
            else:
                messagebox.showerror("错误", str(result))
        except Exception as e:
            messagebox.showerror("错误", f"应用预设失败: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ImageMetadataEditorGUI(root)
        root.mainloop()
    except Exception as e:
        # 如果生错误，显示错误对话框
        import traceback
        error_message = f"程序发生错误：\n{str(e)}\n\n详细信息：\n{traceback.format_exc()}"
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("错误", error_message)
        except:
            # 如果连错误对话框都无法显示，则写入错误日志
            with open("error.log", "w", encoding="utf-8") as f:
                f.write(error_message) 