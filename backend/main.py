from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import shutil

from backend.ocr import ocr_service
from backend.archive_generator import archive_generator
from backend.models import EmployeeInfo

# 创建 FastAPI 应用
app = FastAPI(title="HR Archive Agent")

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建临时文件目录和输出目录
TEMP_DIR = Path("./temp")
TEMP_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ========== 原有接口（保留） ==========
@app.get("/")
def root():
    return {"message": "HR Archive Agent is running"}

@app.get("/health")
def health():
    return {"status": "ok", "ocr_available": ocr_service.ocr is not None}


# ========== 新增接口 ==========
@app.post("/ocr/idcard")
async def recognize_idcard(file: UploadFile = File(...)):
    """识别身份证图片"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    
    try:
        file_ext = Path(file.filename).suffix
        temp_path = TEMP_DIR / f"{uuid.uuid4().hex}{file_ext}"
        
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        result = ocr_service.recognize_id_card(str(temp_path))
        temp_path.unlink()
        
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "识别失败")}
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")


@app.post("/archive/generate")
async def generate_archive(employee: EmployeeInfo):
    """生成员工档案 Word 文件"""
    try:
        employee_dict = employee.dict(exclude_none=True)
        filename = f"{employee.name or 'employee'}_{uuid.uuid4().hex[:8]}.docx"
        output_path = OUTPUT_DIR / filename
        
        success = archive_generator.generate_word(employee_dict, str(output_path))
        
        if not success:
            raise HTTPException(status_code=500, detail="档案生成失败")
        
        return FileResponse(
            path=str(output_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
