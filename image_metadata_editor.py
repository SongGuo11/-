from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os

class ImageMetadataEditor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        
    def get_metadata(self):
        """获取图片的所有元数据"""
        try:
            metadata = {}
            
            # EXIF标签说明
            tag_descriptions = {
                'EXIF_Orientation': '图片方向',
                'EXIF_XResolution': '水平分辨率',
                'EXIF_YResolution': '垂直分辨率',
                'EXIF_ResolutionUnit': '分辨率单位',
                'EXIF_ExifOffset': 'Exif数据偏移量',
                'EXIF_Make': '相机制造商',
                'EXIF_Model': '相机型号',
                'EXIF_Software': '软件',
                'EXIF_DateTime': '修改时间',
                'EXIF_YCbCrPositioning': '色彩位置',
                'EXIF_ExifVersion': 'Exif版本',
                'EXIF_ComponentsConfiguration': '图像构成',
                'EXIF_FlashPixVersion': 'FlashPix版本',
                'EXIF_ColorSpace': '色彩空间',
                'EXIF_ExifImageWidth': '图像宽度',
                'EXIF_ExifImageHeight': '图像高度',
                'EXIF_SceneCaptureType': '场景类型',
                'EXIF_Compression': '压缩方式',
                'EXIF_JPEGInterchangeFormat': 'JPEG数据位置',
                'EXIF_JPEGInterchangeFormatLength': 'JPEG数据长度',
                'EXIF_Artist': '作者',
                'EXIF_Copyright': '版权',
                'EXIF_ImageDescription': '图像描述',
                'EXIF_DateTimeOriginal': '原始拍摄时间',
                'EXIF_DateTimeDigitized': '数字化时间',
                'EXIF_SubSecTime': '秒小数',
                'EXIF_SubSecTimeOriginal': '原始秒小数',
                'EXIF_SubSecTimeDigitized': '数字化秒小数',
                'EXIF_ExposureTime': '曝光时间',
                'EXIF_FNumber': '光圈值',
                'EXIF_ExposureProgram': '曝光程序',
                'EXIF_ISOSpeedRatings': 'ISO感光度',
                'EXIF_SensitivityType': '感光度类型',
                'EXIF_ExifVersion': 'Exif版本',
                'EXIF_DateTimeOriginal': '原始拍摄时间',
                'EXIF_DateTimeDigitized': '数字化时间',
                'EXIF_ComponentsConfiguration': '图像构成',
                'EXIF_CompressedBitsPerPixel': '压缩位深',
                'EXIF_ShutterSpeedValue': '快门速度',
                'EXIF_ApertureValue': '光圈值',
                'EXIF_BrightnessValue': '亮度值',
                'EXIF_ExposureBiasValue': '曝光补偿',
                'EXIF_MaxApertureValue': '最大光圈值',
                'EXIF_SubjectDistance': '主体距离',
                'EXIF_MeteringMode': '测光模式',
                'EXIF_LightSource': '光源',
                'EXIF_Flash': '闪光灯',
                'EXIF_FocalLength': '焦距',
                'EXIF_MakerNote': '制造商注释',
                'EXIF_UserComment': '用户评论',
                'EXIF_SubsecTime': '秒小数',
                'EXIF_SubsecTimeOriginal': '原始秒小数',
                'EXIF_SubsecTimeDigitized': '数字化秒小数',
                'EXIF_FlashPixVersion': 'FlashPix版本',
                'EXIF_ColorSpace': '色彩空间',
                'EXIF_ExifImageWidth': '图像宽度',
                'EXIF_ExifImageHeight': '图像高度',
                'EXIF_InteroperabilityOffset': '互通性偏移量',
                'EXIF_FocalPlaneXResolution': '焦平面水平分辨率',
                'EXIF_FocalPlaneYResolution': '焦平面垂直分辨率',
                'EXIF_FocalPlaneResolutionUnit': '焦平面分辨率单位',
                'EXIF_SensingMethod': '感应方式',
                'EXIF_FileSource': '文件来源',
                'EXIF_SceneType': '场景类型',
                'EXIF_CustomRendered': '自定义图像处理',
                'EXIF_ExposureMode': '曝光模式',
                'EXIF_WhiteBalance': '白平衡',
                'EXIF_DigitalZoomRatio': '数字变焦比率',
                'EXIF_FocalLengthIn35mmFilm': '35mm等效焦距',
                'EXIF_SceneCaptureType': '场景拍摄类型',
                'EXIF_GainControl': '增益控制',
                'EXIF_Contrast': '对比度',
                'EXIF_Saturation': '饱和度',
                'EXIF_Sharpness': '锐度',
                'EXIF_SubjectDistanceRange': '主体距离范围',
                'EXIF_GPSVersionID': 'GPS版本',
                'EXIF_GPSLatitudeRef': '纬度参考',
                'EXIF_GPSLatitude': '纬度',
                'EXIF_GPSLongitudeRef': '经度参考',
                'EXIF_GPSLongitude': '经度',
                'EXIF_GPSAltitudeRef': '高度参考',
                'EXIF_GPSAltitude': '高度',
                'EXIF_GPSTimeStamp': 'GPS时间戳',
                'EXIF_GPSSatellites': 'GPS卫星',
                'EXIF_GPSStatus': 'GPS状态',
                'EXIF_GPSMeasureMode': 'GPS测量模式',
                'EXIF_GPSDOP': 'GPS精度',
                'EXIF_GPSSpeedRef': 'GPS速度参考',
                'EXIF_GPSSpeed': 'GPS速度',
                'EXIF_GPSTrackRef': 'GPS方向参考',
                'EXIF_GPSTrack': 'GPS方向',
                'EXIF_GPSImgDirectionRef': 'GPS图像方向参考',
                'EXIF_GPSImgDirection': 'GPS图像方向',
                'EXIF_GPSMapDatum': 'GPS地图基准',
                'EXIF_GPSDestLatitudeRef': 'GPS目标纬度参考',
                'EXIF_GPSDestLatitude': 'GPS目标纬度',
                'EXIF_GPSDestLongitudeRef': 'GPS目标经度参考',
                'EXIF_GPSDestLongitude': 'GPS目标经度',
                'EXIF_GPSDestBearingRef': 'GPS目标方位参考',
                'EXIF_GPSDestBearing': 'GPS目标方位',
                'EXIF_GPSDestDistanceRef': 'GPS目标距离参考',
                'EXIF_GPSDestDistance': 'GPS目标距离',
                'EXIF_GPSProcessingMethod': 'GPS处理方法',
                'EXIF_GPSAreaInformation': 'GPS区域信息',
                'EXIF_GPSDateStamp': 'GPS日期戳',
                'EXIF_GPSDifferential': 'GPS差分校正'
            }
            
            # 1. 检查 EXIF 数据
            if 'exif' in self.image.info:
                exif_dict = piexif.load(self.image.info['exif'])
                for ifd in exif_dict:
                    if ifd == "thumbnail":
                        continue
                    if isinstance(exif_dict[ifd], dict):
                        for tag_id in exif_dict[ifd]:
                            try:
                                tag = TAGS.get(tag_id, tag_id)
                                value = exif_dict[ifd][tag_id]
                                if isinstance(value, bytes):
                                    try:
                                        value = value.decode('utf-8')
                                    except:
                                        value = str(value)
                                tag_name = f"EXIF_{tag}"
                                description = tag_descriptions.get(tag_name, '')
                                if description:
                                    metadata[f"{tag_name} ({description})"] = value
                                else:
                                    metadata[tag_name] = value
                            except:
                                continue

            # 2. 检查其他元数据
            for key in self.image.info:
                if key not in ['exif'] and not key.startswith('parsed_'):
                    metadata[key] = str(self.image.info[key])
                    
            return metadata if metadata else {"提示": "未找到元数据"}
        except Exception as e:
            return {"错误": f"读取元数据时出错: {str(e)}"}

    def strip_all_metadata(self):
        """彻底清除所有类型的元数据，仅保留像素数据"""
        try:
            # 获取原始图片格式和模式
            original_format = self.image.format
            original_mode = self.image.mode
            
            # 创建新的空白图像
            new_image = Image.new(original_mode, self.image.size)
            # 复制像素数据
            new_image.putdata(list(self.image.getdata()))
            
            # 保存时不包含任何元数据
            temp_path = self.image_path + ".temp"
            save_params = {
                'format': original_format,
                'quality': 95 if original_format == 'JPEG' else None,
            }
            
            # 根据不同格式设置特定参数
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
            
            # 保存新图像
            new_image.save(temp_path, **save_params)
            
            # 关闭图像
            self.image.close()
            new_image.close()
            
            # 替换原文件
            os.replace(temp_path, self.image_path)
            
            # 重新打开图片
            self.image = Image.open(self.image_path)
            
            return True
        except Exception as e:
            return f"清除元数据失败: {str(e)}"

    def save_clean_copy(self, output_path):
        """保存无元数据的副本"""
        try:
            # 获取原始图片格式和模式
            original_format = self.image.format
            original_mode = self.image.mode
            
            # 创建新的空白图像
            new_image = Image.new(original_mode, self.image.size)
            # 复制像素数据
            new_image.putdata(list(self.image.getdata()))
            
            # 保存时不包含任何元数据
            save_params = {
                'format': original_format,
                'quality': 95 if original_format == 'JPEG' else None,
            }
            
            # 根据不同格��设置特定参数
            if original_format == 'JPEG':
                save_params.update({
                    'optimize': False,
                    'exif': b"",
                    'icc_profile': None,
                    'comment': None
                })
            elif original_format == 'PNG':
                save_params.update({
                    'optimize': False,
                    'pnginfo': None
                })
            
            # 保存新图像
            new_image.save(output_path, **save_params)
            new_image.close()
            
            return True
        except Exception as e:
            return f"保存失败: {str(e)}"

    def verify_clean(self, image_path):
        """验证图片是否已清除所有元数据"""
        try:
            with Image.open(image_path) as img:
                # 检查是否存在元数据
                has_exif = 'exif' in img.info
                has_icc = 'icc_profile' in img.info
                has_comment = 'comment' in img.info
                
                return not (has_exif or has_icc or has_comment)
        except:
            return False

    def resize_image(self, new_size, keep_ratio=True, quality=95):
        """调整图片尺寸
        
        Args:
            new_size: (width, height) 新的��寸
            keep_ratio: 是否保持宽高比
            quality: 保存质量（仅对JPEG有效）
        """
        try:
            if keep_ratio:
                # 计算缩放比例，保持宽高比
                ratio = min(new_size[0] / self.image.size[0], new_size[1] / self.image.size[1])
                new_size = (int(self.image.size[0] * ratio), int(self.image.size[1] * ratio))
            
            # 调整尺寸
            resized_image = self.image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 保存时清除所有元数据
            format_mapping = {
                'JPEG': 'JPEG',
                'PNG': 'PNG',
                'GIF': 'GIF',
                'BMP': 'BMP'
            }
            save_format = format_mapping.get(self.image.format, 'JPEG')
            
            if save_format == 'JPEG':
                resized_image.save(
                    self.image_path,
                    format=save_format,
                    quality=quality,
                    optimize=False,
                    exif=b"",
                    icc_profile=None,
                    comment=None,
                    subsampling=0,
                    qtables='keep'
                )
            else:
                resized_image.save(
                    self.image_path,
                    format=save_format,
                    optimize=False,
                    exif=b"",
                    icc_profile=None,
                    comment=None
                )
            
            # 重新打开图像
            self.image = Image.open(self.image_path)
            return True
        except Exception as e:
            return f"调整图片尺寸失败: {str(e)}"

    def crop_image(self, target_size, crop_position='center'):
        """裁剪图片
        
        Args:
            target_size: (width, height) 目标尺寸
            crop_position: 裁剪位置，可选值：
                'center' - 居中裁剪
                'top_left' - 左上角
                'top_right' - 右上角
                'bottom_left' - 左下角
                'bottom_right' - 右下角
        """
        try:
            # 获取原始尺寸
            orig_width, orig_height = self.image.size
            target_width, target_height = target_size
            
            # 计算裁剪区域
            if crop_position == 'center':
                left = (orig_width - target_width) // 2
                top = (orig_height - target_height) // 2
            elif crop_position == 'top_left':
                left = 0
                top = 0
            elif crop_position == 'top_right':
                left = orig_width - target_width
                top = 0
            elif crop_position == 'bottom_left':
                left = 0
                top = orig_height - target_height
            elif crop_position == 'bottom_right':
                left = orig_width - target_width
                top = orig_height - target_height
            
            right = left + target_width
            bottom = top + target_height
            
            # 执行裁剪
            cropped_image = self.image.crop((left, top, right, bottom))
            return cropped_image
        except Exception as e:
            return None

    def update_metadata(self, metadata):
        """更新图片元数据"""
        try:
            # 确保图片文件存在
            if not os.path.exists(self.image_path):
                return f"找不到图片文件: {self.image_path}"

            # 读取现有的EXIF数据
            exif_dict = {'0th': {}, '1st': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}}
            if 'exif' in self.image.info:
                try:
                    exif_dict = piexif.load(self.image.info['exif'])
                except:
                    pass

            # 数据类型转换函数
            def convert_value(value, tag_type):
                try:
                    if tag_type == piexif.TYPES.Ascii:
                        return value.encode('utf-8')
                    elif tag_type == piexif.TYPES.Short:
                        if isinstance(value, str):
                            if '/' in value:  # 处理分数格式
                                num, den = map(int, value.split('/'))
                                return (num, den)
                            return int(value)
                        return value
                    elif tag_type == piexif.TYPES.Long:
                        if isinstance(value, str):
                            return int(value)
                        return value
                    elif tag_type == piexif.TYPES.Rational:
                        if isinstance(value, str):
                            if '/' in value:
                                num, den = map(int, value.split('/'))
                                return (num, den)
                            value = float(value)
                            # 转换为分数形式
                            return (int(value * 100), 100)
                        return value
                    return value
                except:
                    return value

            # 更新元数据
            for field, value in metadata.items():
                # 处理不同类型的字段
                tag_found = False
                for ifd in ['0th', '1st', 'Exif', 'GPS']:
                    for tag_id, tag_info in piexif.TAGS[ifd].items():
                        if tag_info["name"] == field:
                            converted_value = convert_value(value, tag_info["type"])
                            exif_dict[ifd][tag_id] = converted_value
                            tag_found = True
                            break
                    if tag_found:
                        break

                if not tag_found:
                    # 如果找不到对应的标签，尝试作为字符串存储
                    for tag_id, tag_info in piexif.TAGS['0th'].items():
                        if tag_info["type"] == piexif.TYPES.Ascii:
                            exif_dict['0th'][tag_id] = str(value).encode('utf-8')
                            break

            # 保存更新后的EXIF数据
            try:
                exif_bytes = piexif.dump(exif_dict)
                
                # 建临时文件
                temp_path = self.image_path + ".temp"
                self.image.save(temp_path, format=self.image.format, exif=exif_bytes)
                
                # 关闭当前图片
                self.image.close()
                
                # 替换原文件
                os.replace(temp_path, self.image_path)
                
                # 重新打开图片
                self.image = Image.open(self.image_path)
                
                return True
                
            except Exception as e:
                return f"保存EXIF数据失败: {str(e)}"
            
        except Exception as e:
            return f"更新元数据失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    # 修改为您电脑上实际存在的图片路径
    image_path = "test.jpg"
    editor = ImageMetadataEditor(image_path)
    
    # 显示原始元数据
    print("原始元数据:")
    print(editor.get_metadata())
    
    # 清除所有元数据
    result = editor.strip_all_metadata()
    print("\n清除元数据:", "成功" if result == True else result)
    
    # 显示清除后的元数据
    print("\n清除后的元数据:")
    print(editor.get_metadata()) 