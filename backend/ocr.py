"""
OCR 识别模块 - 简化版
使用 PaddleOCR 识别身份证图片
"""

import re
from typing import Dict, Optional

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    print("PaddleOCR not installed. Run: pip install paddleocr")


class OCRService:
    """OCR 识别服务"""
    
    def __init__(self):
        self.ocr = None
        if PADDLE_AVAILABLE:
            try:
                self.ocr = PaddleOCR(
                    lang='ch',
                    use_angle_cls=True
                )
                print("PaddleOCR initialized successfully")
            except Exception as e:
                print(f"PaddleOCR initialization failed: {e}")
                self.ocr = None
        else:
            print("PaddleOCR not available, using mock mode")
    
    def recognize_id_card(self, image_path: str) -> Dict:
        """识别身份证图片"""
        if not self.ocr:
            return self._mock_recognize()
        
        try:
            result = self.ocr.ocr(image_path, cls=True)
            return self._parse_result(result)
        except Exception as e:
            print(f"OCR failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_result(self, ocr_result) -> Dict:
        """解析 OCR 结果"""
        if not ocr_result or not ocr_result[0]:
            return {"success": False, "error": "No text found"}
        
        info = {
            "success": True,
            "name": None,
            "id_card": None,
            "gender": None,
            "birth_date": None,
            "address": None
        }
        
        for line in ocr_result[0]:
            text = line[1][0]
            
            # 姓名
            if "姓名" in text:
                match = re.search(r'姓名[：:\s]*([\u4e00-\u9fa5]{2,4})', text)
                if match:
                    info["name"] = match.group(1)
            
            # 身份证号
            match = re.search(r'[0-9Xx]{15,18}', text)
            if match:
                info["id_card"] = match.group(0).upper()
            
            # 性别
            if "性别" in text:
                match = re.search(r'[男女]', text)
                if match:
                    info["gender"] = match.group(0)
            
            # 出生日期
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
            if match:
                info["birth_date"] = f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
        
        # 从身份证号提取信息
        if info["id_card"] and len(info["id_card"]) == 18:
            if not info["birth_date"]:
                birth = info["id_card"][6:14]
                info["birth_date"] = f"{birth[:4]}-{birth[4:6]}-{birth[6:8]}"
            if not info["gender"]:
                gender_code = int(info["id_card"][16])
                info["gender"] = "男" if gender_code % 2 == 1 else "女"
        
        return info
    
    def _mock_recognize(self) -> Dict:
        """模拟识别"""
        return {
            "success": True,
            "name": "测试员工",
            "id_card": "11010119900307663X",
            "gender": "男",
            "birth_date": "1990-03-07",
            "address": "测试地址"
        }


# 全局实例
ocr_service = OCRService()

