from PIL import Image, ImageDraw

def create_icon(size=(256, 256)):
    # 创建透明背景
    icon = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # 计算尺寸
    width, height = size
    padding = width // 8
    
    # 绘制图片框
    frame_color = (65, 131, 215)  # 蓝色
    frame_points = [
        (padding, padding),  # 左上
        (width - padding, padding),  # 右上
        (width - padding, height - padding),  # 右下
        (padding, height - padding)  # 左下
    ]
    draw.polygon(frame_points, outline=frame_color, width=width//32)
    
    # 绘制元数据符号
    meta_color = (231, 76, 60)  # 红色
    meta_width = width // 3
    meta_height = height // 4
    meta_x = width - padding - meta_width
    meta_y = height - padding - meta_height
    
    # 绘制类似代码的线条
    line_spacing = meta_height // 4
    for i in range(3):
        y = meta_y + i * line_spacing
        # 绘制不同长度的线条
        line_length = meta_width * (0.8 if i == 1 else 1)
        draw.line(
            (meta_x, y, meta_x + line_length, y),
            fill=meta_color,
            width=width//64
        )
    
    # 绘制删除符号
    delete_color = (231, 76, 60)  # 红色
    delete_size = width // 6
    center_x = width // 2
    center_y = height // 2
    
    # 绘制X形
    draw.line(
        (center_x - delete_size, center_y - delete_size,
         center_x + delete_size, center_y + delete_size),
        fill=delete_color,
        width=width//32
    )
    draw.line(
        (center_x - delete_size, center_y + delete_size,
         center_x + delete_size, center_y - delete_size),
        fill=delete_color,
        width=width//32
    )
    
    # 保存不同尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256]
    icon.save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])

if __name__ == '__main__':
    create_icon() 