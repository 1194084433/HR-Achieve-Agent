from pydantic import BaseModel
from typing import Optional, List

"""员工信息模型定义"""

class HonorAndAward(BaseModel):
    """荣誉与奖励记录模型"""
    title: Optional[str] = None #奖项名称
    awarding_organization: Optional[str] = None #颁奖机构
    date: Optional[str] = None #获奖日期
    description: Optional[str] = None #奖项描述

class WorkExperience(BaseModel):
    """工作经历模型"""
    company_name: Optional[str] = None #工作单位
    position: Optional[str] = None #职位
    start_date: Optional[str] = None #开始日期
    end_date: Optional[str] = None #结束日期
    job_description: Optional[str] = None #主要职责

class ProfessionalQualificationCertificate(BaseModel):
    """专业资格证书模型"""
    certificate_name: Optional[str] = None #证书名称
    issuing_authority: Optional[str] = None #发证机关
    acquisition_date: Optional[str] = None #获得日期

class EmployeeInfo(BaseModel):
    """员工信息模型"""
    """员工基本信息"""
    employee_id: Optional[str] = None #员工编号
    name: Optional[str] = None #员工姓名
    age: Optional[int] = None #员工年龄
    ethnicity: Optional[str] = None #民族
    gender: Optional[str] = None #员工性别
    id_card: Optional[str] = None #身份证号
    birth_date: Optional[str] = None #出生日期
    phone: Optional[str] = None #联系电话
    education: Optional[str] = None #学历
    native_place: Optional[str] = None #籍贯
    political_status: Optional[str] = None #政治面貌
    marital_status: Optional[str] = None #婚姻状况
    email: Optional[str] = None #电子邮箱
    emergency_contact: Optional[str] = None #紧急联系人
    emergency_phone: Optional[str] = None #紧急联系电话
    permanent_address: Optional[str] = None #户籍地址
    current_address: Optional[str] = None #现住址
    
    """教育背景信息"""
    date: Optional[str] = None #教育背景日期(from-to)
    school: Optional[str] = None #学校名称
    major: Optional[str] = None #专业
    degree: Optional[str] = None #学历层次
    mode_of_study: Optional[str] = None #学习方式

    """工作经历信息(公司外)"""
    work_experiences: List[WorkExperience] = [] #工作经历列表

    """本公司任职信息"""
    department: Optional[str] = None #部门
    position: Optional[str] = None #岗位名称
    hire_date: Optional[str] = None #入职日期
    job_level: Optional[str] = None #职级
    probation_period: Optional[str] = None #试用期
    monthy_salary: Optional[float] = None #月薪
    contract_type: Optional[str] = None #合同类型
    personnel_file_status: Optional[str] = None #人事档案状态
    social_security_status: Optional[str] = None #社保办理
    housing_fund_status: Optional[str] = None #公积金办理
    contract_duration: Optional[str] = None #合同期限
    status: str = "processing"
    missing_fields: List[str] = []

    """专业资格证书信息"""
    professional_qualifications: List[ProfessionalQualificationCertificate] = []

    """荣誉与奖励记录(入职前)"""
    honors_and_awards: List[HonorAndAward] = []

class OCRResult(BaseModel):
    """OCR 识别结果"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    confidence: float = 0.0