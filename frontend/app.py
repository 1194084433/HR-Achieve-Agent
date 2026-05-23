"""
员工档案批量标准化智能体 - 前端本地模拟版
实现功能：
  1. 管理员登录验证（本地模拟账号密码）
  2. 档案管理：查看列表、新建、重命名、删除（带二次确认）
  3. 员工管理：查看详情、新增、编辑信息、删除员工（带二次确认）
  4. 本地模拟 OCR 识别，自动提取姓名、身份证、性别等结构化信息
  5. 员工信息完整性检测，自动标记缺失字段
  6. 批量上传员工材料，批量识别并自动创建员工档案
  7. 员工档案详情展示、编辑、模拟导出 Word 文档
  8. 多页面路由控制：登录页 → 档案管理页 → 员工管理页
  9. 所有操作本地内存存储，无需后端即可完整演示流程

说明：
  - 本版为【前端独立演示版】，数据全部在前端模拟，不依赖后端
  - 所有标注 TODO 的位置，已预留好对接后端 API 的替换入口
  - 界面交互、流程逻辑与最终上线版本完全一致
  - 密码123456，账号admin
"""

import streamlit as st
from datetime import datetime
import time
import requests  # 后续对接真实后端 API 使用

# ============================================================
# 全局页面配置
# 设置应用标题、图标、布局方式
# ============================================================
st.set_page_config(
    page_title="员工档案批量标准化智能体",
    page_icon="📁",
    layout="wide"
)

# ============================================================
# 初始化 session_state
# 只在应用第一次运行时执行，用于初始化所有跨页面状态变量
# ============================================================
def init_session_state():
    """初始化所有需要跨页面保留的状态变量"""
    # 当前页面路由：login / archive / employee
    if "page" not in st.session_state:
        st.session_state.page = "login"

    # 用户登录状态
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False

    # 档案列表（本地模拟数据）
    if "archives" not in st.session_state:
        st.session_state.archives = [
            {"id": 1, "name": "2025届新员工档案", "count": 2, "created_at": "2025-01-15"},
            {"id": 2, "name": "实习生档案",       "count": 1, "created_at": "2025-03-01"},
            {"id": 3, "name": "社招员工档案",     "count": 0, "created_at": "2025-02-20"},
        ]

    # 当前选中的档案
    if "current_archive" not in st.session_state:
        st.session_state.current_archive = None

    # 当前选中的员工
    if "current_employee" not in st.session_state:
        st.session_state.current_employee = None

    # 员工数据字典（模拟），key=档案ID，value=该档案下员工列表
    # TODO: 后续接入后端后改为从 API 获取
    if "employees_data" not in st.session_state:
        st.session_state.employees_data = {
            1: [
                {"id": 1, "name": "张三", "status": "完整", "id_number": "110101****"},
                {"id": 2, "name": "李四", "status": "缺失", "id_number": "310101****"},
            ],
            2: [
                {"id": 3, "name": "王五", "status": "完整", "id_number": "440101****"},
            ],
            3: []
        }

    # 模拟自增主键，用于新建员工时分配唯一 ID
    if "next_employee_id" not in st.session_state:
        max_id = 0
        for emp_list in st.session_state.employees_data.values():
            for emp in emp_list:
                if emp["id"] > max_id:
                    max_id = emp["id"]
        st.session_state.next_employee_id = max_id + 1

    # 后端接口地址（正式对接时使用）
    if "backend_url" not in st.session_state:
        st.session_state.backend_url = "http://localhost:8000"

    # 档案重命名状态控制
    if "editing_archive_id" not in st.session_state:
        st.session_state.editing_archive_id = None

    # 删除确认状态
    if "deleting_archive_id" not in st.session_state:
        st.session_state.deleting_archive_id = None     # 正在确认删除的档案ID
    if "deleting_employee_id" not in st.session_state:
        st.session_state.deleting_employee_id = None    # 正在确认删除的员工ID

    # 员工详情缓存
    if "employee_detail" not in st.session_state:
        st.session_state.employee_detail = None

    # 编辑模式相关状态
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "edit_data" not in st.session_state:
        st.session_state.edit_data = {}

    # 新建员工流程状态机
    if "new_employee_stage" not in st.session_state:
        st.session_state.new_employee_stage = "idle"
    if "new_employee_uploaded_file" not in st.session_state:
        st.session_state.new_employee_uploaded_file = None
    if "new_employee_recognized_data" not in st.session_state:
        st.session_state.new_employee_recognized_data = {}

    # 批量处理流程状态
    if "batch_stage" not in st.session_state:
        st.session_state.batch_stage = "idle"
    if "batch_files" not in st.session_state:
        st.session_state.batch_files = []
    if "batch_results" not in st.session_state:
        st.session_state.batch_results = []

init_session_state()

# ============================================================
# 数据获取与操作封装函数
# 全部为本地模拟实现，预留 TODO 方便后续替换为后端 API
# ============================================================

def fetch_employees(archive_id):
    """
    获取指定档案下的员工列表
    本地模拟版：直接从内存字典读取
    TODO: 接入后端后改为 GET /api/archives/{archive_id}/employees
    """
    if archive_id not in st.session_state.employees_data:
        st.session_state.employees_data[archive_id] = []
    return st.session_state.employees_data[archive_id]


def fetch_employee_detail(employee_id):
    """
    获取单个员工完整详情信息
    本地模拟版：使用内置模拟数据
    TODO: 接入后端后改为 GET /api/employees/{employee_id}
    """
    # 模拟员工详细信息
    mock_details = {
        1: {"姓名": "张三", "身份证号": "110101199001012345", "性别": "男", "民族": "汉",
            "出生日期": "1990-05-15", "住址": "北京市海淀区中关村南大街5号",
            "手机号": "1386789", "入职日期": "2025-01-15", "部门": "技术部", "职位": "高级工程师"},
        2: {"姓名": "李四", "身份证号": "310101199508211234", "性别": "女", "民族": "汉",
            "出生日期": "1995-08-21", "住址": "", "手机号": "1391234",
            "入职日期": "2025-03-01", "部门": "产品部", "职位": "产品经理"},
        3: {"姓名": "王五", "身份证号": "440101199212011234", "性别": "男", "民族": "汉",
            "出生日期": "1992-12-01", "住址": "广东省广州市天河区", "手机号": "",
            "入职日期": "2025-04-10", "部门": "市场部", "职位": ""},
    }
    return mock_details.get(employee_id, {
        "姓名": "", "身份证号": "", "性别": "", "民族": "",
        "出生日期": "", "住址": "", "手机号": "", "入职日期": "",
        "部门": "", "职位": ""
    })


def save_employee(employee_id, data):
    """
    保存编辑后的员工信息
    本地模拟版：直接返回成功
    TODO: 接入后端后改为 PUT /api/employees/{employee_id}
    """
    return True


def export_employee_archive(employee_id):
    """
    模拟导出员工档案为 Word
    本地版：返回 None，前端提示生成成功
    TODO: 接入后端后改为 GET /api/employees/{id}/export 获取文件流
    """
    return None

# ============================================================
# 模拟 OCR 识别函数
# 本地延迟模拟识别过程，返回固定结构化信息
# TODO: 正式环境替换为真实后端 OCR 接口
# ============================================================
def mock_ocr_recognize(uploaded_file):
    """
    模拟文件 OCR 识别
    输入：上传的图片/PDF/Word
    输出：结构化员工信息
    """
    time.sleep(1.5)
    return {
        "姓名": "赵六",
        "身份证号": "330101199803211234",
        "性别": "男",
        "民族": "汉",
        "出生日期": "1998-03-21",
        "住址": "",
        "手机号": "",
        "入职日期": "",
        "部门": "",
        "职位": "",
    }

# ============================================================
# 页面 1：登录界面
# 本地固定账号密码，用于演示权限控制
# ============================================================
def login_page():
    st.title("📁 员工档案批量标准化智能体")
    st.markdown("---")

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.subheader("🔐 登录系统")
        username = st.text_input("账号", placeholder="请输入账号")
        password = st.text_input("密码", type="password", placeholder="请输入密码")

        if st.button("登录", type="primary", use_container_width=True):
            # 本地模拟登录验证
            if username == "admin" and password == "123456":
                st.session_state.is_logged_in = True
                st.session_state.page = "archive"
                st.success("登录成功，正在跳转...")
                st.rerun()
            else:
                st.error("账号或密码错误")

    st.markdown("---")
    st.caption("v1.0 本地演示版 | 基于 PaddleOCR + 大模型信息抽取")

# ============================================================
# 页面 2：档案管理界面
# 功能：列表展示、重命名、删除（带确认）、新建档案、进入员工管理
# ============================================================
def archive_page():
    st.title("📂 档案管理")

    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.markdown(f"当前共有 **{len(st.session_state.archives)}** 个档案")
    with col_logout:
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.is_logged_in = False
            st.session_state.page = "login"
            st.session_state.current_archive = None
            st.session_state.current_employee = None
            st.rerun()

    st.divider()
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("📋 档案列表")

        for archive in st.session_state.archives:
            # 重命名状态
            if st.session_state.editing_archive_id == archive["id"]:
                new_name = st.text_input("新名称", value=archive["name"], key=f"rename_input_{archive['id']}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 保存", key=f"save_rename_{archive['id']}"):
                        archive["name"] = new_name.strip()
                        st.session_state.editing_archive_id = None
                        st.rerun()
                with col_cancel:
                    if st.button("❌ 取消", key=f"cancel_rename_{archive['id']}"):
                        st.session_state.editing_archive_id = None
                        st.rerun()

            # 删除确认状态
            elif st.session_state.deleting_archive_id == archive["id"]:
                st.warning(f"确定要删除档案「{archive['name']}」吗？该档案下的所有员工也会被删除。")
                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button("✅ 确认删除", key=f"confirm_del_archive_{archive['id']}"):
                        # 本地模拟删除
                        st.session_state.archives.remove(archive)
                        if archive["id"] in st.session_state.employees_data:
                            del st.session_state.employees_data[archive["id"]]
                        st.session_state.deleting_archive_id = None
                        st.success(f"档案「{archive['name']}」已删除")
                        st.rerun()
                with col_cancel:
                    if st.button("❌ 取消", key=f"cancel_del_archive_{archive['id']}"):
                        st.session_state.deleting_archive_id = None
                        st.rerun()

            # 正常展示
            else:
                c_btn, c_name, c_rename, c_delete = st.columns([1, 3, 1, 1])
                with c_btn:
                    if st.button("📁", key=f"open_archive_{archive['id']}", help=f"打开「{archive['name']}」"):
                        st.session_state.current_archive = archive
                        st.session_state.current_employee = None
                        st.session_state.employee_detail = None
                        st.session_state.edit_mode = False
                        st.session_state.new_employee_stage = "idle"
                        st.session_state.batch_stage = "idle"
                        st.session_state.page = "employee"
                        st.rerun()
                with c_name:
                    st.markdown(f"**{archive['name']}**")
                    emp_count = len(fetch_employees(archive["id"]))
                    st.caption(f"{emp_count} 名员工 | 创建于 {archive['created_at']}")
                with c_rename:
                    if st.button("✏️", key=f"edit_archive_{archive['id']}", help="重命名档案"):
                        st.session_state.editing_archive_id = archive["id"]
                        st.rerun()
                with c_delete:
                    if st.button("🗑️", key=f"del_archive_{archive['id']}", help="删除档案"):
                        st.session_state.deleting_archive_id = archive["id"]
                        st.rerun()

            st.divider()

        # 新建档案按钮
        st.markdown("---")
        if st.button("➕ 新建档案", type="primary", use_container_width=True):
            new_id = max([a["id"] for a in st.session_state.archives], default=0) + 1
            new_archive = {
                "id": new_id,
                "name": f"新档案 {new_id}",
                "count": 0,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.archives.append(new_archive)
            st.session_state.current_archive = new_archive
            st.session_state.current_employee = None
            st.session_state.employee_detail = None
            st.session_state.edit_mode = False
            st.session_state.new_employee_stage = "idle"
            st.session_state.batch_stage = "idle"
            st.session_state.page = "employee"
            st.rerun()

    with col_right:
        st.subheader("📊 档案概览")
        if st.session_state.archives:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("档案总数", len(st.session_state.archives))
            with c2:
                total_emp = sum(len(fetch_employees(a["id"])) for a in st.session_state.archives)
                st.metric("员工总数", total_emp)
            with c3:
                st.metric("最近创建", st.session_state.archives[-1]["created_at"])
            st.markdown("---")
            st.markdown("#### 📌 最近档案")
            for a in reversed(st.session_state.archives[-5:]):
                st.markdown(f"- **{a['name']}**（{len(fetch_employees(a['id']))} 人）")
        else:
            st.info("暂无档案，点击「新建档案」开始吧")

# ============================================================
# 页面 3：员工管理界面
# 功能：员工列表、删除确认、详情查看、编辑、新建、批量处理
# ============================================================
def employee_page():
    if st.session_state.current_archive is None:
        st.warning("请先选择档案")
        st.session_state.page = "archive"
        st.rerun()

    archive = st.session_state.current_archive
    employees = fetch_employees(archive["id"])

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"👥 {archive['name']}")
    with col_back:
        if st.button("← 返回档案列表", use_container_width=True):
            st.session_state.page = "archive"
            st.session_state.current_archive = None
            st.session_state.current_employee = None
            st.session_state.employee_detail = None
            st.session_state.edit_mode = False
            st.session_state.new_employee_stage = "idle"
            st.session_state.batch_stage = "idle"
            st.rerun()

    st.divider()
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("👤 员工列表")

        if not employees:
            st.info("该档案下暂无员工，点击下方按钮新建")
        else:
            for emp in employees:
                # 删除确认弹窗
                if st.session_state.deleting_employee_id == emp["id"]:
                    st.warning(f"确定要删除员工「{emp['name']}」吗？")
                    col_c, col_x = st.columns(2)
                    with col_c:
                        if st.button("✅ 确认删除", key=f"confirm_del_emp_{emp['id']}"):
                            archive_id = archive["id"]
                            if archive_id in st.session_state.employees_data:
                                st.session_state.employees_data[archive_id] = [
                                    e for e in st.session_state.employees_data[archive_id]
                                    if e["id"] != emp["id"]
                                ]
                            st.session_state.deleting_employee_id = None
                            if st.session_state.current_employee and st.session_state.current_employee["id"] == emp["id"]:
                                st.session_state.current_employee = None
                                st.session_state.employee_detail = None
                            st.success(f"员工「{emp['name']}」已删除")
                            st.rerun()
                    with col_x:
                        if st.button("❌ 取消", key=f"cancel_del_emp_{emp['id']}"):
                            st.session_state.deleting_employee_id = None
                            st.rerun()
                else:
                    c_btn, c_info, c_del = st.columns([1, 4, 1])
                    with c_btn:
                        if st.button("👤", key=f"emp_{archive['id']}{emp['id']}", help=f"查看 {emp['name']}"):
                            st.session_state.current_employee = emp
                            st.session_state.employee_detail = None
                            st.session_state.edit_mode = False
                            st.session_state.new_employee_stage = "idle"
                            st.session_state.batch_stage = "idle"
                            st.rerun()
                    with c_info:
                        icon = "✅" if emp["status"] == "完整" else "⚠️"
                        st.markdown(f"{icon} **{emp['name']}**")
                        st.caption(f"{emp.get('id_number', '')}")
                    with c_del:
                        if st.button("🗑️", key=f"del_emp{archive['id']}_{emp['id']}", help="删除员工"):
                            st.session_state.deleting_employee_id = emp["id"]
                            st.rerun()
                st.divider()

        st.markdown("---")
        if st.button("➕ 新建员工", use_container_width=True):
            st.session_state.current_employee = None
            st.session_state.employee_detail = None
            st.session_state.edit_mode = False
            st.session_state.batch_stage = "idle"
            st.session_state.new_employee_stage = "upload"
            st.session_state.new_employee_uploaded_file = None
            st.session_state.new_employee_recognized_data = {}
            st.rerun()

        if st.button("📊 批量处理", use_container_width=True):
            st.session_state.current_employee = None
            st.session_state.employee_detail = None
            st.session_state.edit_mode = False
            st.session_state.new_employee_stage = "idle"
            st.session_state.batch_stage = "upload"
            st.session_state.batch_files = []
            st.session_state.batch_results = []
            st.rerun()

    with col_right:
        # 进入新建员工流程
        if st.session_state.new_employee_stage != "idle":
            render_new_employee_flow(archive)
            return

        # 进入批量处理流程
        if st.session_state.batch_stage != "idle":
            render_batch_process_flow(archive)
            return

        # 未选择员工时提示
        if st.session_state.current_employee is None:
            st.info("👈 请从左侧列表选择一名员工查看详情，或点击「新建员工」「批量处理」")
            return

        emp = st.session_state.current_employee

        # 编辑模式
        if st.session_state.edit_mode:
            st.subheader(f"✏️ 编辑 {emp['name']} 的信息")
            edit_data = st.session_state.edit_data

            new_data = {}
            for field, value in edit_data.items():
                new_data[field] = st.text_input(field, value=value)

            col_save_edit, col_cancel_edit = st.columns(2)
            with col_save_edit:
                if st.button("💾 保存修改", type="primary", use_container_width=True):
                    success = save_employee(emp["id"], new_data)
                    if success:
                        st.success("修改已保存（模拟）")
                        st.session_state.employee_detail = new_data
                        st.session_state.edit_mode = False
                        st.rerun()
                    else:
                        st.error("保存失败")
            with col_cancel_edit:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state.edit_mode = False
                    st.rerun()
            return

        # 加载并展示员工详情
        if st.session_state.employee_detail is None:
            with st.spinner("加载员工详情..."):
                detail = fetch_employee_detail(emp["id"])
            st.session_state.employee_detail = detail
        else:
            detail = st.session_state.employee_detail

        st.subheader(f"📋 {emp['name']} 的信息")
        display_data = []
        for field, value in detail.items():
            missing = (not value or str(value).strip() == "")
            display_data.append({
                "字段": field,
                "值": value if not missing else "⚠️ 缺失",
                "状态": "✅" if not missing else "❌"
            })

        st.dataframe(display_data, use_container_width=True, hide_index=True)

        st.markdown("---")
        col_edit, col_preview, col_export = st.columns(3)
        with col_edit:
            if st.button("📝 编辑", use_container_width=True):
                st.session_state.edit_data = detail.copy()
                st.session_state.edit_mode = True
                st.rerun()
        with col_preview:
            if st.button("👁️ 预览", use_container_width=True):
                st.info("预览档案格式（功能开发中）")
        with col_export:
            if st.button("📥 导出", use_container_width=True, type="primary"):
                with st.spinner("正在生成档案..."):
                    file_content = export_employee_archive(emp["id"])
                    if file_content:
                        st.download_button(
                            label="⬇️ 下载档案",
                            data=file_content,
                            file_name=f"员工档案_{emp['name']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    else:
                        st.success(f"员工档案_{emp['name']}.docx 已生成（模拟）")

# ============================================================
# 新建员工流程
# 分为上传文件 → OCR 识别 → 信息确认 → 创建员工
# ============================================================
def render_new_employee_flow(archive):
    stage = st.session_state.new_employee_stage

    if stage == "upload":
        st.subheader("➕ 新建员工 - 上传入职材料")
        st.markdown("请上传员工的入职文件（图片、PDF、Word 文档均可），系统将自动识别提取信息。")

        uploaded_file = st.file_uploader(
            "支持 jpg, jpeg, png, pdf, docx, doc",
            type=["jpg", "jpeg", "png", "pdf", "docx", "doc"],
            key="new_employee_file_uploader"
        )

        if uploaded_file:
            st.session_state.new_employee_uploaded_file = uploaded_file
            if uploaded_file.type and uploaded_file.type.startswith("image"):
                st.image(uploaded_file, caption="上传的文件预览", width=400)
            else:
                st.info(f"已上传文件：{uploaded_file.name}（{uploaded_file.size // 1024} KB）")

        can_recognize = st.session_state.new_employee_uploaded_file is not None
        if st.button("🔍 开始识别", type="primary", disabled=not can_recognize):
            with st.spinner("正在识别中，请稍候..."):
                recognized = mock_ocr_recognize(st.session_state.new_employee_uploaded_file)
            st.session_state.new_employee_recognized_data = recognized
            st.session_state.new_employee_stage = "confirm"
            st.rerun()

        if st.button("❌ 取消"):
            st.session_state.new_employee_stage = "idle"
            st.rerun()

    elif stage == "confirm":
        st.subheader("📋 确认员工信息")
        st.markdown("以下是自动识别的结果，请核对并补全缺失字段。")

        data = st.session_state.new_employee_recognized_data
        completed_data = {}
        for field, value in data.items():
            col_label, col_input = st.columns([1, 3])
            with col_label:
                st.markdown(f"**{field}**")
            with col_input:
                if value == "":
                    completed_data[field] = st.text_input(f"{field}（必填）", "", key=f"new_emp_{field}", placeholder="请输入...")
                else:
                    completed_data[field] = st.text_input(field, value, key=f"new_emp_{field}")

        st.markdown("---")
        col_confirm, col_back, col_cancel = st.columns(3)
        with col_confirm:
            if st.button("✅ 确认创建", type="primary", use_container_width=True):
                empty_fields = [k for k, v in completed_data.items() if v.strip() == ""]
                if empty_fields:
                    st.warning(f"以下字段仍为空，但允许创建：{', '.join(empty_fields)}")

                new_id = st.session_state.next_employee_id
                st.session_state.next_employee_id += 1

                has_missing = any(v.strip() == "" for v in completed_data.values())
                status = "缺失" if has_missing else "完整"

                new_employee = {
                    "id": new_id,
                    "name": completed_data.get("姓名", "未知"),
                    "status": status,
                    "id_number": completed_data.get("身份证号", "")[:6] + "****"
                }

                archive_id = archive["id"]
                if archive_id not in st.session_state.employees_data:
                    st.session_state.employees_data[archive_id] = []
                st.session_state.employees_data[archive_id].append(new_employee)

                st.success(f"员工「{new_employee['name']}」创建成功！")
                st.session_state.new_employee_stage = "idle"
                st.session_state.new_employee_uploaded_file = None
                st.session_state.new_employee_recognized_data = {}
                st.rerun()

        with col_back:
            if st.button("↩ 返回上传", use_container_width=True):
                st.session_state.new_employee_stage = "upload"
                st.session_state.new_employee_recognized_data = {}
                st.rerun()

        with col_cancel:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.new_employee_stage = "idle"
                st.session_state.new_employee_uploaded_file = None
                st.session_state.new_employee_recognized_data = {}
                st.rerun()

# ============================================================
# 批量处理流程
# 支持多文件上传 → 批量 OCR → 批量入库 → 结果展示
# ============================================================
def render_batch_process_flow(archive):
    stage = st.session_state.batch_stage

    if stage == "upload":
        st.subheader("📊 批量处理 - 上传入职材料")
        st.markdown("可一次性上传多个员工的入职文件，系统自动逐个识别并创建档案。")

        uploaded_files = st.file_uploader(
            "支持 jpg, jpeg, png, pdf, docx, doc，可多选",
            type=["jpg", "jpeg", "png", "pdf", "docx", "doc"],
            accept_multiple_files=True,
            key="batch_file_uploader"
        )

        if uploaded_files:
            st.session_state.batch_files = uploaded_files
            st.info(f"已选择 {len(uploaded_files)} 个文件")
            for i, f in enumerate(uploaded_files, 1):
                st.markdown(f"{i}. {f.name}（{f.size // 1024} KB）")

        can_start = len(st.session_state.batch_files) > 0
        col_start, col_cancel = st.columns(2)
        with col_start:
            if st.button("🚀 开始批量处理", type="primary", disabled=not can_start, use_container_width=True):
                st.session_state.batch_stage = "processing"
                st.session_state.batch_results = []
                st.rerun()
        with col_cancel:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.batch_stage = "idle"
                st.session_state.batch_files = []
                st.rerun()

    elif stage == "processing":
        st.subheader("⏳ 批量处理中...")
        files = st.session_state.batch_files
        total = len(files)
        progress_bar = st.progress(0)
        status_text = st.empty()

        results = st.session_state.batch_results

        if len(results) < total:
            current_index = len(results)
            current_file = files[current_index]
            status_text.text(f"正在处理第 {current_index + 1}/{total} 个文件：{current_file.name}...")
            progress_bar.progress(current_index / total)

            try:
                recognized = mock_ocr_recognize(current_file)
                has_name = recognized.get("姓名", "") != ""
                if has_name:
                    new_id = st.session_state.next_employee_id
                    st.session_state.next_employee_id += 1
                    new_emp = {
                        "id": new_id,
                        "name": recognized.get("姓名", "未知"),
                        "status": "完整" if all(v != "" for v in recognized.values()) else "缺失",
                        "id_number": recognized.get("身份证号", "")[:6] + "****"
                    }
                    archive_id = archive["id"]
                    if archive_id not in st.session_state.employees_data:
                        st.session_state.employees_data[archive_id] = []
                    st.session_state.employees_data[archive_id].append(new_emp)

                    results.append({
                        "filename": current_file.name,
                        "status": "成功",
                        "message": f"已创建员工：{new_emp['name']}"
                    })
                else:
                    results.append({
                        "filename": current_file.name,
                        "status": "失败",
                        "message": "未能识别到姓名"
                    })
            except Exception as e:
                results.append({
                    "filename": current_file.name,
                    "status": "失败",
                    "message": str(e)
                })

            st.session_state.batch_results = results
            time.sleep(0.5)
            st.rerun()
        else:
            progress_bar.progress(1.0)
            status_text.text(f"全部处理完毕！共 {total} 个文件。")
            st.session_state.batch_stage = "done"
            st.rerun()

    elif stage == "done":
        st.subheader("✅ 批量处理完成")
        results = st.session_state.batch_results

        success_count = sum(1 for r in results if r["status"] == "成功")
        fail_count = len(results) - success_count

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("文件总数", len(results))
        with col2:
            st.metric("成功", success_count)
        with col3:
            st.metric("失败", fail_count)

        st.markdown("---")
        st.markdown("#### 处理明细")
        for i, r in enumerate(results, 1):
            icon = "✅" if r["status"] == "成功" else "❌"
            st.markdown(f"{icon} **{i}. {r['filename']}** — {r['message']}")

        st.markdown("---")
        col_done, col_retry = st.columns(2)
        with col_done:
            if st.button("👍 完成", type="primary", use_container_width=True):
                st.session_state.batch_stage = "idle"
                st.session_state.batch_files = []
                st.session_state.batch_results = []
                st.rerun()
        with col_retry:
            if st.button("🔄 重新批量处理", use_container_width=True):
                st.session_state.batch_stage = "upload"
                st.session_state.batch_files = []
                st.session_state.batch_results = []
                st.rerun()

# ============================================================
# 全局路由控制
# 根据登录状态与当前页面变量渲染对应界面
# ============================================================
if not st.session_state.is_logged_in:
    login_page()
else:
    if st.session_state.page == "archive":
        archive_page()
    elif st.session_state.page == "employee":
        employee_page()
    else:
        st.session_state.page = "archive"
        archive_page()
