"""
格式验证和规范化模块
提供日期、手机号、身份证号等字段的格式校验和规范化功能
"""

import re
from typing import Tuple, Optional


class Validator:
    """格式验证和规范化工具类"""
    
    @staticmethod
    def normalize_date(date_str: str) -> Tuple[Optional[str], bool]:
        """
        规范化日期格式为 YYYY-MM-DD
        
        Args:
            date_str: 原始日期字符串
            
        Returns:
            (规范化后的日期, 是否有效)
        """
        if not date_str:
            return None, False
        
        # 移除空格
        cleaned = str(date_str).strip()
        
        # 匹配 YYYY-MM-DD
        match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', cleaned)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}", True
        
        # 匹配 YYYY年MM月DD日
        match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', cleaned)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}", True
        
        # 匹配 YYYYMMDD
        match = re.match(r'(\d{4})(\d{2})(\d{2})', cleaned)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}", True
        
        return date_str, False
    
    @staticmethod
    def normalize_phone(phone_str: str) -> Tuple[Optional[str], bool]:
        """
        规范化手机号：提取数字，校验11位以1开头
        
        Args:
            phone_str: 原始手机号字符串
            
        Returns:
            (规范化后的手机号, 是否有效)
        """
        if not phone_str:
            return None, False
        
        # 提取所有数字
        digits = re.sub(r'\D', '', str(phone_str))
        
        # 中国手机号：11位，以1开头
        if len(digits) == 11 and digits.startswith('1'):
            return digits, True
        
        return digits if digits else None, False
    
    @staticmethod
    def normalize_id_card(id_card_str: str) -> Tuple[Optional[str], bool]:
        """
        规范化身份证号：去除空格，统一大写，校验长度
        
        Args:
            id_card_str: 原始身份证号字符串
            
        Returns:
            (规范化后的身份证号, 是否有效)
        """
        if not id_card_str:
            return None, False
        
        # 去除空格，转大写
        cleaned = re.sub(r'\s', '', str(id_card_str)).upper()
        
        # 18位身份证
        if len(cleaned) == 18:
            if re.match(r'^\d{17}[\dX]$', cleaned):
                return cleaned, True
        # 15位身份证
        elif len(cleaned) == 15:
            if re.match(r'^\d{15}$', cleaned):
                return cleaned, True
        
        return cleaned, False
    
    @staticmethod
    def validate_id_card_checksum(id_card: str) -> bool:
        """
        校验18位身份证的校验码
        
        Args:
            id_card: 18位身份证号
            
        Returns:
            bool: 校验码是否正确
        """
        if not id_card or len(id_card) != 18:
            return False
        
        # 加权因子
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        # 校验码对应值
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        total = 0
        for i, ch in enumerate(id_card[:17]):
            if not ch.isdigit():
                return False
            total += int(ch) * factors[i]
        
        expected = check_codes[total % 11]
        return id_card[17] == expected
    
    @staticmethod
    def check_missing_fields(data: dict, required_fields: list) -> list:
        """
        检查必填字段是否缺失
        
        Args:
            data: 待检查的数据字典
            required_fields: 必填字段列表
            
        Returns:
            list: 缺失的字段名列表
        """
        missing = []
        for field in required_fields:
            value = data.get(field)
            if not value or str(value).strip() == '':
                missing.append(field)
        return missing


# 全局实例
validator = Validator()


# 常用的必填字段清单
COMMON_REQUIRED_FIELDS = [
    'name',           # 姓名
    'id_card',        # 身份证号
    'phone',          # 手机号
    'hire_date',      # 入职日期
]