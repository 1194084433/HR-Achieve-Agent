"""
简历解析模块
支持 PDF/DOCX 格式的简历文件，提取完整的员工信息
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import tempfile

# PDF 处理
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# DOCX 处理
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# OCR（用于扫描版PDF）
try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class ResumeParser:
    """简历解析器 - 提取完整的员工信息"""
    
    def __init__(self):
        self.ocr = None
        if OCR_AVAILABLE:
            try:
                self.ocr = PaddleOCR(lang='ch', use_angle_cls=True, show_log=False)
                print("✅ PaddleOCR 初始化成功")
            except Exception as e:
                print(f"⚠️ PaddleOCR 初始化失败: {e}")
    
    def parse_resume(self, file_path: str) -> Dict:
        """
        解析简历文件，提取完整的员工信息
        
        Args:
            file_path: 简历文件路径（PDF 或 DOCX）
            
        Returns:
            Dict: 符合 EmployeeInfo 模型结构的员工信息
        """
        file_ext = Path(file_path).suffix.lower()
        
        # 提取原始文本
        if file_ext == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            text = self._extract_from_docx(file_path)
        else:
            return {"success": False, "error": f"不支持的文件格式: {file_ext}"}
        
        if not text:
            return {"success": False, "error": "无法提取文件内容"}
        
        # 从文本中提取完整信息
        info = self._extract_full_info(text)
        info["success"] = True
        
        return info
    
    def _extract_from_pdf(self, pdf_path: str) -> str:
        """从 PDF 文件中提取文字"""
        text = ""
        
        if PDF_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"PyPDF2 提取失败: {e}")
        
        # 如果没有提取到文字，使用 OCR
        if not text.strip() and self.ocr:
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, dpi=200)
                for img in images:
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        img.save(tmp.name, 'PNG')
                        result = self.ocr.ocr(tmp.name, cls=True)
                        Path(tmp.name).unlink()
                        if result and result[0]:
                            for line in result[0]:
                                text += line[1][0] + "\n"
            except Exception as e:
                print(f"OCR 识别 PDF 失败: {e}")
        
        return text
    
    def _extract_from_docx(self, docx_path: str) -> str:
        """从 DOCX 文件中提取文字"""
        if not DOCX_AVAILABLE:
            return ""
        
        try:
            doc = Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"DOCX 提取失败: {e}")
            return ""
    
    def _extract_full_info(self, text: str) -> Dict:
        """
        从文本中提取完整的员工信息
        
        Args:
            text: 简历文本
            
        Returns:
            Dict: 完整的员工信息
        """
        info = {
            # === 基本信息 ===
            "name": None,
            "gender": None,
            "birth_date": None,
            "phone": None,
            "email": None,
            "ethnicity": None,           # 民族
            "native_place": None,        # 籍贯
            "political_status": None,    # 政治面貌
            "marital_status": None,      # 婚姻状况
            "id_card": None,             # 身份证号
            "permanent_address": None,   # 户籍地址
            "current_address": None,     # 现住址
            "emergency_contact": None,   # 紧急联系人
            "emergency_phone": None,     # 紧急联系电话
            
            # === 教育背景 ===
            "education_backgrounds": [],
            
            # === 工作经历 ===
            "work_experiences": [],
            
            # === 本公司任职信息 ===
            "department": None,
            "position": None,
            "hire_date": None,
            "job_level": None,
            
            # === 专业资格证书 ===
            "professional_qualifications": [],
            
            # === 荣誉与奖励 ===
            "honors_and_awards": [],
            
            # === 其他 ===
            "education": None,   # 最高学历
            "school": None,      # 毕业院校
            "major": None,       # 专业
            "graduation_date": None,  # 毕业时间
            "skills": None,      # 技能特长
        }
        
        # ========== 1. 提取基本信息 ==========
        
        # 姓名（2-4个中文字符，通常在文本开头几行）
        lines = text.strip().split('\n')
        for line in lines[:15]:
            name_match = re.match(r'^([\u4e00-\u9fa5]{2,4})$', line.strip())
            if name_match:
                info["name"] = name_match.group(1)
                break
        
        # 性别
        gender_match = re.search(r'性别[：:\s]*([男女])', text)
        if gender_match:
            info["gender"] = gender_match.group(1)
        
        # 出生日期（多种格式）
        birth_patterns = [
            r'出生日期[：:\s]*(\d{4})[-年](\d{1,2})[-月](\d{1,2})',
            r'生日[：:\s]*(\d{4})[-年](\d{1,2})[-月](\d{1,2})',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
        ]
        for pattern in birth_patterns:
            match = re.search(pattern, text)
            if match:
                year, month, day = match.group(1), match.group(2), match.group(3)
                info["birth_date"] = f"{year}-{int(month):02d}-{int(day):02d}"
                break
        
        # 手机号
        phone_match = re.search(r'1[3-9]\d{9}', text)
        if phone_match:
            info["phone"] = phone_match.group(0)
        
        # 邮箱
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            info["email"] = email_match.group(0)
        
        # 民族
        ethnicity_match = re.search(r'民族[：:\s]*([\u4e00-\u9fa5]{1,5}族)', text)
        if ethnicity_match:
            info["ethnicity"] = ethnicity_match.group(1)
        
        # 籍贯
        native_match = re.search(r'籍贯[：:\s]*([\u4e00-\u9fa5]{2,20})', text)
        if native_match:
            info["native_place"] = native_match.group(1)
        
        # 政治面貌
        political_match = re.search(r'政治面貌[：:\s]*(党员|共青团员|群众|民主党派)', text)
        if political_match:
            info["political_status"] = political_match.group(1)
        
        # 婚姻状况
        marital_match = re.search(r'婚姻状况[：:\s]*(已婚|未婚|离异|丧偶)', text)
        if marital_match:
            info["marital_status"] = marital_match.group(1)
        
        # 身份证号
        id_match = re.search(r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]', text)
        if id_match:
            info["id_card"] = id_match.group(0).upper()
        
        # 地址
        address_match = re.search(r'地址[：:\s]*([^\n]{5,50})', text)
        if address_match:
            info["permanent_address"] = address_match.group(1)
        
        # ========== 2. 提取教育背景 ==========
        
        # 匹配教育经历段落
        edu_section = self._extract_section(text, r'教育背景|教育经历|学历')
        
        # 学校
        school_match = re.search(r'([\u4e00-\u9fa5]{2,20}(大学|学院|学校|研究院))', text)
        if school_match:
            info["school"] = school_match.group(1)
        
        # 专业
        major_match = re.search(r'专业[：:\s]*([\u4e00-\u9fa5]{2,20})', text)
        if not major_match:
            major_match = re.search(r'([\u4e00-\u9fa5]{2,20}工程|[\u4e00-\u9fa5]{2,20}技术|[\u4e00-\u9fa5]{2,20}管理|[\u4e00-\u9fa5]{2,20}科学)', text)
        if major_match:
            info["major"] = major_match.group(1)
        
        # 学历层次
        degree_keywords = ['博士', '硕士', '研究生', '本科', '大专', '专科', 'MBA']
        for degree in degree_keywords:
            if degree in text:
                info["education"] = degree
                break
        
        # 毕业时间
        grad_match = re.search(r'毕业时间[：:\s]*(\d{4})', text)
        if not grad_match:
            grad_match = re.search(r'(\d{4})年毕业', text)
        if grad_match:
            info["graduation_date"] = f"{grad_match.group(1)}-06-30"
        
        # 多段教育背景
        edu_entries = self._extract_education_entries(text)
        if edu_entries:
            info["education_backgrounds"] = edu_entries
        
        # ========== 3. 提取工作经历 ==========
        
        # 岗位/职位
        position_match = re.search(r'应聘职位[：:\s]*([^\n]+)', text)
        if not position_match:
            position_match = re.search(r'职位[：:\s]*([^\n]+)', text)
        if position_match:
            info["position"] = position_match.group(1).strip()
        
        # 工作经历列表
        work_entries = self._extract_work_entries(text)
        if work_entries:
            info["work_experiences"] = work_entries
        
        # 部门（根据职位推断）
        dept_map = {
            '开发': '技术部', '工程师': '技术部', '程序员': '技术部',
            '产品': '产品部', '运营': '运营部', '销售': '销售部',
            '人事': '人力资源部', '财务': '财务部', '市场': '市场部'
        }
        if info["position"]:
            for key, dept in dept_map.items():
                if key in info["position"]:
                    info["department"] = dept
                    break
        
        # ========== 4. 提取专业资格证书 ==========
        
        cert_section = self._extract_section(text, r'证书|资格认证|专业技能')
        cert_entries = self._extract_certificates(cert_section if cert_section else text)
        if cert_entries:
            info["professional_qualifications"] = cert_entries
        
        # ========== 5. 提取荣誉与奖励 ==========
        
        honor_section = self._extract_section(text, r'荣誉|奖励|获奖|表彰')
        honor_entries = self._extract_honors(honor_section if honor_section else text)
        if honor_entries:
            info["honors_and_awards"] = honor_entries
        
        # 技能
        skills_match = re.search(r'技能特长[：:\s]*([^\n]{5,200})', text)
        if not skills_match:
            skills_match = re.search(r'专业技能[：:\s]*([^\n]{5,200})', text)
        if skills_match:
            info["skills"] = skills_match.group(1)
        
        return info
    
    def _extract_section(self, text: str, pattern: str) -> str:
        """提取指定章节的内容"""
        match = re.search(f'{pattern}[：:\s]*\n?([\s\S]{0,500})', text)
        if match:
            return match.group(1)
        return ""
    
    def _extract_education_entries(self, text: str) -> List[Dict]:
        """提取多段教育经历"""
        entries = []
        
        # 匹配时间模式：2015-2019 或 2015年-2019年
        patterns = [
            r'(\d{4})[-~至](\d{4})\s+([\u4e00-\u9fa5]{2,20}(?:大学|学院|学校))\s+([\u4e00-\u9fa5]{2,20})',
            r'(\d{4})年[-~至](\d{4})年\s+([\u4e00-\u9fa5]{2,20}(?:大学|学院|学校))\s+([\u4e00-\u9fa5]{2,20})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                start_year, end_year, school, major = match
                entries.append({
                    "period": f"{start_year}-{end_year}",
                    "school": school,
                    "major": major,
                    "degree": None,
                    "mode_of_study": None
                })
        
        return entries
    
    def _extract_work_entries(self, text: str) -> List[Dict]:
        """提取多段工作经历"""
        entries = []
        
        # 匹配工作经历模式
        patterns = [
            r'(\d{4})[-~至](\d{4}|至今|现在)\s+([\u4e00-\u9fa5a-zA-Z0-9]{2,30}(?:科技|有限|公司|集团)?)\s+([^\n]{2,30}?(?:经理|工程师|专员|总监|主管))',
            r'(\d{4})年[-~至](\d{4}|至今|现在)年\s+([\u4e00-\u9fa5]{2,20}(?:公司|集团)?)\s+([^\n]{2,20})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                start_year, end_year, company, position = match
                end_date = end_year if end_year in ['至今', '现在'] else end_year
                entries.append({
                    "company_name": company.strip(),
                    "position": position.strip(),
                    "start_date": f"{start_year}-01-01" if len(start_year) == 4 else start_year,
                    "end_date": "至今" if end_date in ['至今', '现在'] else (f"{end_date}-12-31" if len(end_date) == 4 else end_date),
                    "job_description": ""
                })
        
        return entries
    
    def _extract_certificates(self, text: str) -> List[Dict]:
        """提取专业资格证书"""
        entries = []
        
        # 常见证书关键词
        cert_keywords = ['证书', '资格证', '认证', 'PMP', 'CPA', 'CET', '英语', '计算机']
        
        for keyword in cert_keywords:
            if keyword in text:
                # 提取包含关键词的行
                lines = text.split('\n')
                for line in lines:
                    if keyword in line:
                        entries.append({
                            "certificate_name": line.strip()[:50],
                            "issuing_authority": None,
                            "acquisition_date": None
                        })
        
        # 去重
        seen = set()
        unique_entries = []
        for entry in entries:
            if entry["certificate_name"] not in seen:
                seen.add(entry["certificate_name"])
                unique_entries.append(entry)
        
        return unique_entries[:10]  # 最多10个
    
    def _extract_honors(self, text: str) -> List[Dict]:
        """提取荣誉与奖励"""
        entries = []
        
        # 匹配奖励模式
        patterns = [
            r'获[得]{0,1}[ ]{0,}([\u4e00-\u9fa5]{2,30}(?:奖|称号|优秀))',
            r'荣获[\s]*([\u4e00-\u9fa5]{2,30}(?:奖|称号))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entries.append({
                    "title": match if isinstance(match, str) else match[0],
                    "awarding_organization": None,
                    "date": None,
                    "description": None
                })
        
        # 去重
        seen = set()
        unique_entries = []
        for entry in entries:
            if entry["title"] not in seen:
                seen.add(entry["title"])
                unique_entries.append(entry)
        
        return unique_entries[:10]


resume_parser = ResumeParser()

